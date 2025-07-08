from google.cloud import documentai_v1 as documentai
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from pdf2image import convert_from_path
import io


def find_keyword_positions(document, keyword):
    positions = []
    checked_ranges = set()  # (start_index, end_index) 튜플 저장
    for page_idx, page in enumerate(document.pages):
        tokens = page.tokens
        token_texts = []
        print(f"[DEBUG] tokens: {len(tokens)}")
        for token in tokens:
            start = int(token.layout.text_anchor.text_segments[0].start_index)
            end = int(token.layout.text_anchor.text_segments[0].end_index)
            token_texts.append((document.text[start:end], token, start, end))
            print(f"[DEBUG] token_texts: {document.text[start:end]}")
        for i in range(len(token_texts)):
            for j in range(i, min(i + len(keyword), len(token_texts))):
                combined_text = ''.join([t[0] for t in token_texts[i:j+1]])
                start_idx = token_texts[i][2]
                end_idx = token_texts[j][3]
                # 조합 텍스트가 keyword와 정확히 일치할 때만 처리
                if combined_text == keyword and (start_idx, end_idx) not in checked_ranges:
                    print(f"[DEBUG] 페이지 {page_idx+1}, 조합 텍스트: {combined_text}")
                    checked_ranges.add((start_idx, end_idx))
                    # 키워드가 포함된 모든 토큰의 바운딩 박스를 합쳐서 전체 범위 계산
                    all_vertices = []
                    for k in range(i, j+1):
                        token_vertices = token_texts[k][1].layout.bounding_poly.vertices
                        all_vertices.extend(token_vertices)
                    # 전체 범위의 바운딩 박스 계산
                    if all_vertices:
                        x_coords = [v.x for v in all_vertices]
                        y_coords = [v.y for v in all_vertices]
                        min_x, max_x = min(x_coords), max(x_coords)
                        min_y, max_y = min(y_coords), max(y_coords)
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
                            "text": combined_text
                        })
                    break  # 일치하는 조합을 찾으면 더 긴 조합은 검사하지 않음
    return positions


def add_bounding_box_to_pdf(input_pdf_path, output_pdf_path, positions):
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
        page_positions = [pos for pos in positions if pos["page"] == page_num]
        if page_positions:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))

            for pos in page_positions:
                vertices = pos["vertices"]
                if len(vertices) >= 4:
                    # 좌표 보정 적용
                    x_coords = [v.x * scale_x for v in vertices]
                    y_coords = [page_height - (v.y * scale_y) for v in vertices]  # y축 반전
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    width = x_max - x_min
                    height = y_max - y_min
                    print(f"[DEBUG] PDF 보정 좌표: x_min={x_min:.2f}, y_min={y_min:.2f}, width={width:.2f}, height={height:.2f}")
                    can.setStrokeColor(Color(1, 0, 0, alpha=1))
                    can.setFillColor(Color(1, 0, 0, alpha=0.1))
                    can.setLineWidth(2)
                    can.rect(x_min, y_min, width, height, fill=1, stroke=1)
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
