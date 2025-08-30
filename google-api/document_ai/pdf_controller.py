from google.cloud import documentai_v1 as documentai
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from pdf2image import convert_from_path
import io


def find_keyword_positions(document, keyword):
    print(f"[DEBUG] document: {type(document)}")
    positions = []
    checked_ranges = set()  # (start_index, end_index) 튜플 저장
    keyword_nospace = keyword.replace(' ', '')
    
    for page_idx, page in enumerate(document.pages):
        tokens = page.tokens
        token_texts = []
        print(f"[DEBUG] 페이지 {page_idx+1}, 토큰 수: {len(tokens)}")
        
        # 모든 토큰의 텍스트와 좌표 정보 수집
        for token in tokens:
            if hasattr(token, 'layout') and hasattr(token.layout, 'text_anchor') and token.layout.text_anchor.text_segments:
                start = int(token.layout.text_anchor.text_segments[0].start_index)
                end = int(token.layout.text_anchor.text_segments[0].end_index)
                token_text = document.text[start:end]
                token_texts.append((token_text, token, start, end))
        
        print(f"[DEBUG] 페이지 {page_idx+1}, 처리할 토큰 수: {len(token_texts)}")
        
        # 키워드 검색 및 매칭
        for i in range(len(token_texts)):
            for j in range(i, min(i + len(keyword_nospace) + 2, len(token_texts))):
                combined_text = ''.join([t[0] for t in token_texts[i:j+1]])
                combined_text_nospace = combined_text.replace(' ', '')
                start_idx = token_texts[i][2]
                end_idx = token_texts[j][3]
                
                # 공백 제거 후 텍스트에 keyword가 포함되어 있으면 처리 (정확히 일치할 필요 없음)
                if keyword_nospace in combined_text_nospace and (start_idx, end_idx) not in checked_ranges:
                    print(f"[DEBUG] 페이지 {page_idx+1}, 키워드 포함 발견: '{combined_text}' (토큰 {i+1}~{j+1})")
                    checked_ranges.add((start_idx, end_idx))
                    
                    # 키워드가 포함된 모든 토큰의 바운딩 박스를 합쳐서 전체 범위 계산
                    all_vertices = []
                    for k in range(i, j+1):
                        if hasattr(token_texts[k][1], 'layout') and hasattr(token_texts[k][1].layout, 'bounding_poly'):
                            token_vertices = token_texts[k][1].layout.bounding_poly.vertices
                            if token_vertices:
                                all_vertices.extend(token_vertices)
                    
                    # 전체 범위의 바운딩 박스 계산
                    if all_vertices:
                        x_coords = [v.x for v in all_vertices]
                        y_coords = [v.y for v in all_vertices]
                        min_x, max_x = min(x_coords), max(x_coords)
                        min_y, max_y = min(y_coords), max(y_coords)
                        
                        # 여백 추가 (키워드 주변에 약간의 여백을 주어 가독성 향상)
                        margin = 5
                        min_x = max(0, min_x - margin)
                        min_y = max(0, min_y - margin)
                        max_x = max_x + margin
                        max_y = max_y + margin
                        
                        from google.cloud import documentai_v1
                        bounding_vertices = [
                            documentai_v1.Vertex(x=min_x, y=min_y),
                            documentai_v1.Vertex(x=max_x, y=min_y),
                            documentai_v1.Vertex(x=max_x, y=max_y),
                            documentai_v1.Vertex(x=min_x, y=max_y)
                        ]
                        
                        positions.append({
                            "page": page_idx,
                            "vertices": bounding_vertices,
                            "keyword": keyword,
                            "text": combined_text,
                            "bbox": (min_x, min_y, max_x, max_y),
                            "token_range": (i+1, j+1)
                        })
                        
                        print(f"[DEBUG] 바운딩 박스: ({min_x:.1f}, {min_y:.1f}) ~ ({max_x:.1f}, {max_y:.1f})")
                    break  # 일치하는 조합을 찾으면 더 긴 조합은 검사하지 않음
    
    print(f"[DEBUG] 총 {len(positions)}개의 키워드 위치를 찾았습니다.")
    return positions


def add_bounding_box_to_pdf(input_pdf_path, output_pdf_path, positions):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # PDF 첫 페이지에서 mediabox 크기
    page = reader.pages[0]
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    print(f"[DEBUG] PDF mediabox: width={page_width}, height={page_height}")

    # Document AI 좌표계와 PDF 좌표계 간의 정확한 변환을 위한 스케일 팩터 계산
    try:
        # pdf2image로 PDF를 이미지로 변환 (Document AI와 동일한 해상도로)
        images = convert_from_path(input_pdf_path, first_page=1, last_page=1, dpi=300)
        if images:
            img_width, img_height = images[0].size
            print(f"[DEBUG] PDF image size: width={img_width}, height={img_height}")
            
            # 스케일 팩터 계산 (Document AI 좌표 → PDF 좌표)
            scale_x = page_width / img_width
            scale_y = page_height / img_height
            print(f"[DEBUG] 원본 스케일 팩터: scale_x={scale_x:.6f}, scale_y={scale_y:.6f}")
            
            # 스케일 팩터 보정 (텍스트 bbox가 너무 작은 문제 해결)
            correction_factor = 1.15  # 15% 확장
            scale_x *= correction_factor
            scale_y *= correction_factor
            print(f"[DEBUG] 보정된 스케일 팩터: scale_x={scale_x:.6f}, scale_y={scale_y:.6f}")
            
            # 스케일 팩터가 너무 크거나 작으면 경고
            if abs(scale_x - scale_y) > 0.001:
                print(f"[WARNING] X, Y 스케일 팩터가 다릅니다. 정확도에 영향을 줄 수 있습니다.")
                # 평균 스케일 팩터 사용
                avg_scale = (scale_x + scale_y) / 2
                scale_x = scale_y = avg_scale
                print(f"[INFO] 평균 스케일 팩터 사용: {avg_scale:.6f}")
        else:
            print("[WARNING] 이미지 변환 실패, 스케일 팩터를 1.0으로 설정")
            scale_x = scale_y = 1.0
    except Exception as e:
        print(f"[WARNING] pdf2image 변환 실패: {e}, 스케일 팩터를 1.0으로 설정")
        scale_x = scale_y = 1.0

    for page_num, page in enumerate(reader.pages):
        page_positions = [pos for pos in positions if pos["page"] == page_num]
        if page_positions:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))

            for pos in page_positions:
                vertices = pos["vertices"]
                if len(vertices) >= 4:
                    # 좌표 보정 적용 (더 정확한 변환)
                    x_coords = [v.x * scale_x for v in vertices]
                    y_coords = [page_height - (v.y * scale_y) for v in vertices]  # y축 반전
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    # 바운딩 박스 여백 확장 (텍스트가 잘리지 않도록)
                    margin_x = 10  # x축 여백
                    margin_y = 5  # y축 여백 (한글 텍스트는 y축이 더 중요)
                    
                    # 여백을 적용한 최종 바운딩 박스 계산
                    final_x_min = max(0, x_min - margin_x)
                    final_y_min = max(0, y_min - margin_y)
                    final_x_max = min(page_width, x_max + margin_x)
                    final_y_max = min(page_height, y_max + margin_y)
                    
                    width = final_x_max - final_x_min
                    height = final_y_max - final_y_min
                    
                    print(f"[DEBUG] 키워드: {pos.get('keyword', 'N/A')}")
                    print(f"[DEBUG] 원본 좌표: {[(v.x, v.y) for v in vertices]}")
                    print(f"[DEBUG] 변환된 좌표: x_min={x_min:.2f}, y_min={y_min:.2f}, x_max={x_max:.2f}, y_max={y_max:.2f}")
                    print(f"[DEBUG] 여백 적용 후: x_min={final_x_min:.2f}, y_min={final_y_min:.2f}, width={width:.2f}, height={height:.2f}")
                    
                    can.setStrokeColor(Color(1, 0, 0, alpha=1))
                    can.setFillColor(Color(1, 0, 0, alpha=0.1))
                    can.setLineWidth(2)
                    can.rect(final_x_min, final_y_min, width, height, fill=1, stroke=1)
            can.save()
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"바운딩 박스가 추가된 PDF가 {output_pdf_path}에 저장되었습니다.")

def print_text_positions(positions):
    if not positions:
        print("찾은 텍스트가 없습니다.")
        return
    print(f"\n총 {len(positions)}개의 키워드를 찾았습니다:")
    for i, pos in enumerate(positions, 1):
        print(
            f"\n{i}. 페이지 {pos['page'] + 1}"
            f"   좌표: {pos['vertices']}"
            f"   좌표: {type(pos['vertices'])}"
            f"   텍스트: {pos['text']}"
        )


def visualize_blocks_and_paragraphs(input_pdf_path, output_pdf_path, document):
    """Document의 모든 block과 paragraph 영역을 시각화"""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # PDF 첫 페이지에서 mediabox 크기
    page = reader.pages[0]
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    print(f"[DEBUG] PDF mediabox: width={page_width}, height={page_height}")

    # pdf2image를 사용해서 PDF를 이미지로 변환하고 크기 추출
    try:
        images = convert_from_path(input_pdf_path, first_page=1, last_page=1)
        if images:
            img_width, img_height = images[0].size
            print(f"[DEBUG] PDF image size: width={img_width}, height={img_height}")
            
            # 스케일 팩터 계산
            scale_x = page_width / img_width
            scale_y = page_height / img_height
            print(f"[DEBUG] scale_x={scale_x}, scale_y={scale_y}")
        else:
            print("[WARNING] 이미지 변환 실패, 스케일 팩터를 1.0으로 설정")
            scale_x = scale_y = 1.0
    except Exception as e:
        print(f"[WARNING] pdf2image 변환 실패: {e}, 스케일 팩터를 1.0으로 설정")
        scale_x = scale_y = 1.0

    for page_num, page in enumerate(reader.pages):
        if page_num < len(document.pages):
            doc_page = document.pages[page_num]
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # Block들을 파란색으로 표시
            for block_idx, block in enumerate(doc_page.blocks):
                if hasattr(block, 'layout') and hasattr(block.layout, 'bounding_poly'):
                    vertices = block.layout.bounding_poly.vertices
                    if len(vertices) >= 4:
                        # 좌표 보정 적용
                        x_coords = [v.x * scale_x for v in vertices]
                        y_coords = [page_height - (v.y * scale_y) for v in vertices]  # y축 반전
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        width = x_max - x_min
                        height = y_max - y_min
                        
                        # Block은 파란색 박스로 표시
                        can.setStrokeColor(Color(0, 0, 1, alpha=1))  # 파란색
                        can.setFillColor(Color(0, 0, 1, alpha=0.1))  # 연한 파란색
                        can.setLineWidth(1)
                        can.rect(x_min, y_min, width, height, fill=1, stroke=1)
                        
                        # Block 번호 표시
                        can.setFillColor(Color(0, 0, 1, alpha=1))
                        can.setFont("Helvetica", 6)
                        can.drawString(x_min, y_min - 3, f"B{block_idx}")

            # Paragraph들을 초록색으로 표시
            for para_idx, paragraph in enumerate(doc_page.paragraphs):
                if hasattr(paragraph, 'layout') and hasattr(paragraph.layout, 'bounding_poly'):
                    vertices = paragraph.layout.bounding_poly.vertices
                    if len(vertices) >= 4:
                        # 좌표 보정 적용
                        x_coords = [v.x * scale_x for v in vertices]
                        y_coords = [page_height - (v.y * scale_y) for v in vertices]  # y축 반전
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        width = x_max - x_min
                        height = y_max - y_min
                        
                        # Paragraph는 초록색 박스로 표시
                        can.setStrokeColor(Color(0, 1, 0, alpha=1))  # 초록색
                        can.setFillColor(Color(0, 1, 0, alpha=0.1))  # 연한 초록색
                        can.setLineWidth(1)
                        can.rect(x_min, y_min, width, height, fill=1, stroke=1)
                        
                        # Paragraph 번호 표시
                        can.setFillColor(Color(0, 1, 0, alpha=1))
                        can.setFont("Helvetica", 6)
                        can.drawString(x_min, y_min - 8, f"P{para_idx}")
            
            can.save()
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Block과 Paragraph 영역이 시각화된 PDF가 {output_pdf_path}에 저장되었습니다.")


def extract_and_save_text_by_units(document, output_dir="outputs"):
    """Document의 block과 paragraph 텍스트를 추출하여 파일로 저장"""
    import os
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # Block 텍스트 추출 및 저장
    block_texts = []
    for page_idx, page in enumerate(document.pages):
        for block_idx, block in enumerate(page.blocks):
            # Block의 bounding_poly 영역에 해당하는 텍스트를 tokens에서 추출
            if hasattr(block, 'layout') and hasattr(block.layout, 'bounding_poly'):
                block_vertices = block.layout.bounding_poly.vertices
                if len(block_vertices) >= 4:
                    # Block 영역의 좌표 범위 계산
                    x_coords = [v.x for v in block_vertices]
                    y_coords = [v.y for v in block_vertices]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    # 해당 영역에 포함되는 tokens 찾기
                    block_text = ""
                    for token in page.tokens:
                        if hasattr(token, 'layout') and hasattr(token.layout, 'bounding_poly'):
                            token_vertices = token.layout.bounding_poly.vertices
                            if len(token_vertices) >= 4:
                                token_x_coords = [v.x for v in token_vertices]
                                token_y_coords = [v.y for v in token_vertices]
                                token_x_min, token_x_max = min(token_x_coords), max(token_x_coords)
                                token_y_min, token_y_max = min(token_y_coords), max(token_y_coords)
                                
                                # Token이 Block 영역에 포함되는지 확인
                                if (token_x_min >= x_min and token_x_max <= x_max and 
                                    token_y_min >= y_min and token_y_max <= y_max):
                                    # text_anchor를 사용하여 텍스트 추출
                                    if hasattr(token.layout, 'text_anchor') and token.layout.text_anchor.text_segments:
                                        start_idx = int(token.layout.text_anchor.text_segments[0].start_index)
                                        end_idx = int(token.layout.text_anchor.text_segments[0].end_index)
                                        token_text = document.text[start_idx:end_idx]
                                        block_text += token_text + " "
                    
                    block_texts.append({
                        "page": page_idx + 1,
                        "block": block_idx + 1,
                        "text": block_text.strip(),
                        "confidence": getattr(block, 'confidence', 'N/A'),
                        "coordinates": f"({x_min:.1f}, {y_min:.1f}) to ({x_max:.1f}, {y_max:.1f})"
                    })
    
    # Block 텍스트를 파일로 저장
    with open(f"{output_dir}/blocks_text.txt", "w", encoding="utf-8") as f:
        f.write("=== BLOCK 단위 텍스트 ===\n\n")
        for block_info in block_texts:
            f.write(f"페이지 {block_info['page']}, Block {block_info['block']}\n")
            f.write(f"좌표: {block_info['coordinates']}\n")
            f.write(f"신뢰도: {block_info['confidence']}\n")
            f.write(f"텍스트: {block_info['text']}\n")
            f.write("-" * 50 + "\n\n")
    
    print(f"Block 텍스트가 {output_dir}/blocks_text.txt에 저장되었습니다.")
    
    # Paragraph 텍스트 추출 및 저장
    paragraph_texts = []
    for page_idx, page in enumerate(document.pages):
        for para_idx, paragraph in enumerate(page.paragraphs):
            # Paragraph의 bounding_poly 영역에 해당하는 텍스트를 tokens에서 추출
            if hasattr(paragraph, 'layout') and hasattr(paragraph.layout, 'bounding_poly'):
                para_vertices = paragraph.layout.bounding_poly.vertices
                if len(para_vertices) >= 4:
                    # Paragraph 영역의 좌표 범위 계산
                    x_coords = [v.x for v in para_vertices]
                    y_coords = [v.y for v in para_vertices]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    # 해당 영역에 포함되는 tokens 찾기
                    para_text = ""
                    for token in page.tokens:
                        if hasattr(token, 'layout') and hasattr(token.layout, 'bounding_poly'):
                            token_vertices = token.layout.bounding_poly.vertices
                            if len(token_vertices) >= 4:
                                token_x_coords = [v.x for v in token_vertices]
                                token_y_coords = [v.y for v in token_vertices]
                                token_x_min, token_x_max = min(token_x_coords), max(token_x_coords)
                                token_y_min, token_y_max = min(token_y_coords), max(token_y_coords)
                                
                                # Token이 Paragraph 영역에 포함되는지 확인
                                if (token_x_min >= x_min and token_x_max <= x_max and 
                                    token_y_min >= y_min and token_y_max <= y_max):
                                    # text_anchor를 사용하여 텍스트 추출
                                    if hasattr(token.layout, 'text_anchor') and token.layout.text_anchor.text_segments:
                                        start_idx = int(token.layout.text_anchor.text_segments[0].start_index)
                                        end_idx = int(token.layout.text_anchor.text_segments[0].end_index)
                                        token_text = document.text[start_idx:end_idx]
                                        para_text += token_text + " "
                    
                    paragraph_texts.append({
                        "page": page_idx + 1,
                        "paragraph": para_idx + 1,
                        "text": para_text.strip(),
                        "confidence": getattr(paragraph, 'confidence', 'N/A'),
                        "coordinates": f"({x_min:.1f}, {y_min:.1f}) to ({x_max:.1f}, {y_max:.1f})"
                    })
    
    # Paragraph 텍스트를 파일로 저장
    with open(f"{output_dir}/paragraphs_text.txt", "w", encoding="utf-8") as f:
        f.write("=== PARAGRAPH 단위 텍스트 ===\n\n")
        for para_info in paragraph_texts:
            f.write(f"페이지 {para_info['page']}, Paragraph {para_info['paragraph']}\n")
            f.write(f"좌표: {para_info['coordinates']}\n")
            f.write(f"신뢰도: {para_info['confidence']}\n")
            f.write(f"텍스트: {para_info['text']}\n")
            f.write("-" * 50 + "\n\n")
    
    print(f"Paragraph 텍스트가 {output_dir}/paragraphs_text.txt에 저장되었습니다.")
    
    # 요약 정보 출력
    print(f"\n=== 요약 ===")
    print(f"총 페이지 수: {len(document.pages)}")
    print(f"총 Block 수: {len(block_texts)}")
    print(f"총 Paragraph 수: {len(paragraph_texts)}")
    
    return block_texts, paragraph_texts


def split_pdf_by_pages(input_pdf_path, max_pages_per_chunk=5):
    """
    PDF를 최대 5페이지 단위로 잘라서 byte list를 만드는 함수
    
    Args:
        input_pdf_path (str): 입력 PDF 파일 경로
        max_pages_per_chunk (int): 청크당 최대 페이지 수 (기본값: 5)
    
    Returns:
        list: PDF byte 데이터의 리스트
    """
    try:
        # PDF 파일 읽기
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        
        print(f"[INFO] PDF 총 페이지 수: {total_pages}")
        print(f"[INFO] 청크당 최대 페이지 수: {max_pages_per_chunk}")
        
        # 청크 수 계산
        num_chunks = (total_pages + max_pages_per_chunk - 1) // max_pages_per_chunk
        print(f"[INFO] 총 청크 수: {num_chunks}")
        
        pdf_chunks = []
        
        for chunk_idx in range(num_chunks):
            # 현재 청크의 시작과 끝 페이지 계산
            start_page = chunk_idx * max_pages_per_chunk
            end_page = min(start_page + max_pages_per_chunk, total_pages)
            
            print(f"[INFO] 청크 {chunk_idx + 1}: 페이지 {start_page + 1} ~ {end_page}")
            
            # 새로운 PDF Writer 생성
            from PyPDF2 import PdfWriter
            writer = PdfWriter()
            
            # 지정된 페이지 범위의 페이지들 추가
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # PDF를 byte로 변환
            pdf_bytes = io.BytesIO()
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            
            # byte 데이터를 리스트에 추가
            pdf_chunks.append({
                "chunk_index": chunk_idx,
                "start_page": start_page + 1,
                "end_page": end_page,
                "page_count": end_page - start_page,
                "content": pdf_bytes.getvalue()
            })
            
            print(f"[INFO] 청크 {chunk_idx + 1} 생성 완료: {len(pdf_bytes.getvalue())} bytes")
        
        print(f"[INFO] 모든 청크 생성 완료. 총 {len(pdf_chunks)}개 청크")
        return pdf_chunks
        
    except Exception as e:
        print(f"[ERROR] PDF 분할 중 오류 발생: {e}")
        return []


def extract_bordered_region_to_pdf(input_image_path, output_pdf_path, border_thickness=3, min_area=1000):
    """
    이미지에서 테두리가 있는 네모 공간을 추출해서 그 영역만 PDF로 만드는 함수
    
    Args:
        input_image_path (str): 입력 이미지 파일 경로
        output_pdf_path (str): 출력 PDF 파일 경로
        border_thickness (int): 테두리 두께 (기본값: 3)
        min_area (int): 최소 영역 크기 (기본값: 1000)
    """
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        import cv2
        
        # 이미지 로드
        print(f"[INFO] 이미지 로드 중: {input_image_path}")
        image = cv2.imread(input_image_path)
        if image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {input_image_path}")
        
        # BGR을 RGB로 변환
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이진화 (흑백으로 변환)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"[INFO] 발견된 윤곽선 수: {len(contours)}")
        
        # 사각형 윤곽선 필터링
        rectangular_contours = []
        for i, contour in enumerate(contours):
            # 윤곽선을 근사화하여 사각형인지 확인
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 4개의 꼭지점을 가진 윤곽선 (사각형)
            if len(approx) == 4:
                # 면적 계산
                area = cv2.contourArea(contour)
                if area > min_area:
                    # 사각형의 직각성 확인
                    rect = cv2.minAreaRect(contour)
                    width, height = rect[1]
                    aspect_ratio = max(width, height) / min(width, height)
                    
                    # 너무 길쭉한 사각형 제외 (aspect_ratio < 5)
                    if aspect_ratio < 5:
                        rectangular_contours.append({
                            'contour': contour,
                            'approx': approx,
                            'area': area,
                            'rect': rect
                        })
                        print(f"[INFO] 사각형 {i+1}: 면적={area:.0f}, 비율={aspect_ratio:.2f}")
        
        if not rectangular_contours:
            print("[WARNING] 적절한 사각형 테두리를 찾을 수 없습니다.")
            return False
        
        # 가장 큰 사각형 선택 (일반적으로 메인 콘텐츠 영역)
        rectangular_contours.sort(key=lambda x: x['area'], reverse=True)
        main_contour = rectangular_contours[0]
        
        print(f"[INFO] 선택된 메인 사각형: 면적={main_contour['area']:.0f}")
        
        # 사각형의 꼭지점 좌표 추출
        approx = main_contour['approx']
        points = approx.reshape(4, 2)
        
        # 좌표를 정렬 (좌상단, 우상단, 우하단, 좌하단 순서)
        # x, y 좌표의 합과 차를 이용하여 정렬
        points = sorted(points, key=lambda p: (p[1], p[0]))  # y, x 순서로 정렬
        
        # 좌상단, 우상단, 우하단, 좌하단 순서로 재배열
        if points[0][0] > points[1][0]:  # 첫 번째 두 점의 x 좌표 비교
            points[0], points[1] = points[1], points[0]
        if points[2][0] < points[3][0]:  # 마지막 두 점의 x 좌표 비교
            points[2], points[3] = points[3], points[2]
        
        # 투시 변환을 위한 목표 좌표 계산
        # 원본 사각형의 너비와 높이 계산
        width = max(np.linalg.norm(points[1] - points[0]), np.linalg.norm(points[2] - points[3]))
        height = max(np.linalg.norm(points[3] - points[0]), np.linalg.norm(points[2] - points[1]))
        
        # 정수로 변환
        width = int(width)
        height = int(height)
        
        # 목표 좌표 (정사각형으로 변환)
        dst_points = np.array([
            [0, 0],           # 좌상단
            [width, 0],       # 우상단
            [width, height],  # 우하단
            [0, height]       # 좌하단
        ], dtype=np.float32)
        
        # 투시 변환 행렬 계산
        src_points = np.array(points, dtype=np.float32)
        transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # 투시 변환 적용
        warped = cv2.warpPerspective(image, transform_matrix, (width, height))
        
        # RGB로 변환
        warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
        
        # PIL 이미지로 변환
        pil_warped = Image.fromarray(warped_rgb)
        
        # PDF로 저장
        print(f"[INFO] PDF 저장 중: {output_pdf_path}")
        pil_warped.save(output_pdf_path, "PDF", resolution=300.0)
        
        print(f"[SUCCESS] 테두리 영역이 추출되어 PDF로 저장되었습니다: {output_pdf_path}")
        print(f"[INFO] 추출된 영역 크기: {width} x {height} pixels")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 테두리 영역 추출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_bordered_region_with_preview(input_image_path, output_pdf_path, preview_path=None):
    """
    테두리 영역 추출 + 미리보기 이미지 생성
    
    Args:
        input_image_path (str): 입력 이미지 파일 경로
        output_pdf_path (str): 출력 PDF 파일 경로
        preview_path (str): 미리보기 이미지 파일 경로 (선택사항)
    """
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        import cv2
        
        # 이미지 로드
        print(f"[INFO] 이미지 로드 중: {input_image_path}")
        image = cv2.imread(input_image_path)
        if image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {input_image_path}")
        
        # 원본 이미지 복사 (미리보기용)
        preview_image = image.copy()
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이진화
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 모폴로지 연산
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 사각형 윤곽선 필터링 및 미리보기에 표시
        rectangular_contours = []
        for i, contour in enumerate(contours):
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:
                area = cv2.contourArea(contour)
                if area > 1000:
                    rect = cv2.minAreaRect(contour)
                    width, height = rect[1]
                    aspect_ratio = max(width, height) / min(width, height)
                    
                    if aspect_ratio < 5:
                        rectangular_contours.append({
                            'contour': contour,
                            'approx': approx,
                            'area': area,
                            'rect': rect
                        })
                        
                        # 미리보기에 사각형 그리기
                        color = (0, 255, 0) if i == 0 else (0, 0, 255)  # 첫 번째는 초록색, 나머지는 빨간색
                        cv2.drawContours(preview_image, [approx], -1, color, 2)
                        
                        # 면적과 번호 표시
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m10"] / M["m00"])
                            cv2.putText(preview_image, f"{i+1}:{area:.0f}", (cx-20, cy), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 미리보기 이미지 저장
        if preview_path:
            preview_rgb = cv2.cvtColor(preview_image, cv2.COLOR_BGR2RGB)
            preview_pil = Image.fromarray(preview_rgb)
            preview_pil.save(preview_path)
            print(f"[INFO] 미리보기 이미지 저장: {preview_path}")
        
        # 가장 큰 사각형 선택하여 PDF 생성
        if rectangular_contours:
            rectangular_contours.sort(key=lambda x: x['area'], reverse=True)
            main_contour = rectangular_contours[0]
            
            # PDF 생성 로직 (이전 함수와 동일)
            approx = main_contour['approx']
            points = approx.reshape(4, 2)
            points = sorted(points, key=lambda p: (p[1], p[0]))
            
            if points[0][0] > points[1][0]:
                points[0], points[1] = points[1], points[0]
            if points[2][0] < points[3][0]:
                points[2], points[3] = points[3], points[2]
            
            width = int(max(np.linalg.norm(points[1] - points[0]), np.linalg.norm(points[2] - points[3])))
            height = int(max(np.linalg.norm(points[3] - points[0]), np.linalg.norm(points[2] - points[1])))
            
            dst_points = np.array([
                [0, 0], [width, 0], [width, height], [0, height]
            ], dtype=np.float32)
            
            src_points = np.array(points, dtype=np.float32)
            transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            
            warped = cv2.warpPerspective(image, transform_matrix, (width, height))
            warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            pil_warped = Image.fromarray(warped_rgb)
            
            # PDF 저장
            pil_warped.save(output_pdf_path, "PDF", resolution=300.0)
            print(f"[SUCCESS] 테두리 영역이 추출되어 PDF로 저장되었습니다: {output_pdf_path}")
            
            return True
        else:
            print("[WARNING] 적절한 사각형 테두리를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"[ERROR] 테두리 영역 추출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

