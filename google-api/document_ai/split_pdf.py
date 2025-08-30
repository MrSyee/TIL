from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader, PdfWriter
import io
import argparse
import os
import cv2
from PIL import Image, ImageDraw
import numpy as np
import uuid

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1

from dotenv import load_dotenv

load_dotenv()


def save_debug_image(image_bgr, page_idx, main_contour=None, is_no_border=False):
    """
    디버깅용 이미지를 저장하는 함수
    
    Args:
        image_bgr: BGR 형식의 이미지
        page_idx: 페이지 인덱스
        main_contour: 메인 사각형 윤곽선 정보 (None이면 테두리 없음)
        is_no_border: 테두리가 없는 경우 True
    
    Note:
        이 함수는 extract_bordered_region_to_pdf 함수에서 enable_debug=True일 때만 호출됩니다.
        디버깅을 비활성화하려면 enable_debug=False로 설정하세요.
    """
    debug_image = image_bgr.copy()
    
    if is_no_border:
        # 테두리가 없는 경우 경고 메시지 표시
        warning_text = f"Page {page_idx + 1}: No borders found"
        cv2.putText(debug_image, warning_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        suffix = "_no_border"
    else:
        # 메인 사각형 윤곽선 그리기 (빨간색, 두께 3)
        cv2.drawContours(debug_image, [main_contour['contour']], -1, (0, 0, 255), 3)
        
        # 꼭지점 그리기 (파란색 원)
        for i, point in enumerate(main_contour['approx']):
            x, y = point[0]
            cv2.circle(debug_image, (x, y), 5, (255, 0, 0), -1)
            # 꼭지점 번호 표시
            cv2.putText(debug_image, str(i+1), (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # 면적 정보와 점수 표시
        area_text = f"Area: {main_contour['area']:.0f}"
        cv2.putText(debug_image, area_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if 'total_score' in main_contour:
            score_text = f"Score: {main_contour['total_score']:.3f}"
            cv2.putText(debug_image, score_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 세부 점수 정보도 표시
            center_text = f"Center: {main_contour['center_score']:.3f}"
            cv2.putText(debug_image, center_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            size_text = f"Size: {main_contour['size_score']:.3f}"
            cv2.putText(debug_image, size_text, (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        suffix = ""
    
    # 디버깅 이미지 저장
    os.makedirs("outputs/contours", exist_ok=True)
    unique_id = str(uuid.uuid4())[:8]  # 8자리 유니크 ID
    debug_filename = f"outputs/contours/{page_idx + 1:03d}_{unique_id}{suffix}.jpg"
    cv2.imwrite(debug_filename, debug_image)
    print(f"[DEBUG] 디버깅 이미지 저장: {debug_filename}")


def extract_bordered_region_to_pdf(pdf_bytes, output_pdf_path=None, border_thickness=3, min_area=1000, enable_debug=True):
    """
    PDF byte에서 테두리가 있는 네모 공간을 추출해서 그 영역만 PDF로 만드는 함수
    
    Args:
        pdf_bytes (bytes): 입력 PDF byte 데이터
        output_pdf_path (str): 출력 PDF 파일 경로 (선택사항, None이면 파일 저장 안함)
        border_thickness (int): 테두리 두께 (기본값: 3)
        min_area (int): 최소 영역 크기 (기본값: 1000)
        enable_debug (bool): 디버깅 이미지 저장 여부 (기본값: True)
    
    Returns:
        bytes: 추출된 영역의 PDF byte 데이터 (실패시 None)
    """
    try:
        # PDF byte를 이미지로 변환
        print(f"[INFO] PDF byte 처리 중: {len(pdf_bytes)} bytes")
        
        # PDF를 이미지로 변환 (모든 페이지)
        images = convert_from_bytes(pdf_bytes, dpi=600)  # 더 높은 해상도 (600 DPI)
        if not images:
            raise ValueError("PDF를 이미지로 변환할 수 없습니다")
        
        print(f"[INFO] 총 {len(images)}페이지를 처리합니다")
        
        # 모든 페이지에서 추출된 이미지들을 저장할 리스트
        extracted_images = []
        
        for page_idx, image in enumerate(images):
            print(f"[INFO] 페이지 {page_idx + 1} 처리 중...")
            
            # PIL 이미지를 numpy array로 변환
            image_np = np.array(image)
            
            # RGB를 BGR로 변환 (OpenCV는 BGR 사용)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # 그레이스케일 변환
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # 이진화 (흑백으로 변환)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 모폴로지 연산으로 노이즈 제거 및 테두리 연결
            # 더 큰 커널로 테두리 연결 강화
            kernel_close = np.ones((5, 5), np.uint8)  # 테두리 연결용
            kernel_open = np.ones((3, 3), np.uint8)   # 노이즈 제거용
            
            # 먼저 테두리 연결 (CLOSE 연산)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
            # 그 다음 노이즈 제거 (OPEN 연산)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open)
            
            # 추가로 테두리를 더 두껍게 만들어 연결 강화
            kernel_dilate = np.ones((2, 2), np.uint8)
            binary = cv2.dilate(binary, kernel_dilate, iterations=1)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print(f"[INFO] 페이지 {page_idx + 1}: 발견된 윤곽선 수 {len(contours)}")
            
            # 사각형 윤곽선 필터링
            rectangular_contours = []
            image_height, image_width = image_bgr.shape[:2]
            total_image_area = image_width * image_height
            
            for i, contour in enumerate(contours):
                # 윤곽선을 근사화하여 사각형인지 확인
                # 더 관대한 근사화로 끊어진 테두리도 인식
                epsilon = 0.05 * cv2.arcLength(contour, True)  # 0.02 -> 0.05로 증가
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # 4~6개의 꼭지점을 가진 윤곽선 허용 (끊어진 테두리 고려)
                if 4 <= len(approx) <= 6:
                    # 면적 계산
                    area = cv2.contourArea(contour)
                    if area > min_area:
                        # 사각형의 직각성 확인
                        rect = cv2.minAreaRect(contour)
                        width, height = rect[1]
                        aspect_ratio = max(width, height) / min(width, height)
                        
                        # 너무 길쭉한 사각형 제외 (aspect_ratio < 5)
                        if aspect_ratio < 5:
                            # 경계 사각형 계산
                            x, y, w, h = cv2.boundingRect(contour)
                            bounding_area = w * h
                            
                            # 페이지 경계에서 너무 가까운 contour 제외
                            margin = 30
                            if (x < margin or y < margin or 
                                x + w > image_width - margin or 
                                y + h > image_height - margin):
                                print(f"[DEBUG] 페이지 {page_idx + 1}, 사각형 {i+1}: 페이지 경계 너무 가까움")
                                continue
                            
                            # 너무 작은 사각형 제외 (페이지의 0.5% 미만)
                            area_ratio = area / total_image_area
                            if area_ratio < 0.005:
                                print(f"[DEBUG] 페이지 {page_idx + 1}, 사각형 {i+1}: 너무 작음 (면적 비율: {area_ratio:.3%})")
                                continue
                            
                            # 너무 큰 사각형 제외 (페이지의 90% 이상)
                            if area_ratio > 0.9:
                                print(f"[DEBUG] 페이지 {page_idx + 1}, 사각형 {i+1}: 너무 큼 (면적 비율: {area_ratio:.3%})")
                                continue
                            
                            rectangular_contours.append({
                                'contour': contour,
                                'approx': approx,
                                'area': area,
                                'rect': rect,
                                'bounding_area': bounding_area,
                                'area_ratio': area_ratio,
                                'bounding_rect': (x, y, w, h)
                            })
                            print(f"[INFO] 페이지 {page_idx + 1}, 사각형 {i+1}: 면적={area:.0f}, 경계면적={bounding_area:.0f}, 비율={aspect_ratio:.2f}, 면적비율={area_ratio:.3%}")
            
            if not rectangular_contours:
                print(f"[WARNING] 페이지 {page_idx + 1}에서 적절한 사각형 테두리를 찾을 수 없습니다.")
                
                # 디버깅용: 테두리가 없는 경우 원본 이미지에 경고 메시지 표시
                if enable_debug:
                    save_debug_image(image_bgr, page_idx, is_no_border=True)
                
                # 테두리가 없는 경우 원본 이미지 사용
                extracted_images.append(image)
                continue
            
            # 스마트한 사각형 선택 (면적, 위치, 형태를 종합적으로 고려)
            # 답안 영역은 보통 페이지 중앙에 있고 적당한 크기를 가짐
            for contour_info in rectangular_contours:
                x, y, w, h = contour_info['bounding_rect']
                
                # 중앙 위치 점수 계산 (페이지 중앙에 가까울수록 높은 점수)
                center_x = x + w // 2
                center_y = y + h // 2
                page_center_x = image_width // 2
                page_center_y = image_height // 2
                distance_from_center = np.sqrt((center_x - page_center_x)**2 + (center_y - page_center_y)**2)
                max_distance = np.sqrt(page_center_x**2 + page_center_y**2)
                center_score = 1.0 - (distance_from_center / max_distance)
                
                # 적절한 크기 점수 계산 (너무 작거나 크지 않은 적당한 크기일 때 높은 점수)
                area_ratio = contour_info['area_ratio']
                if area_ratio < 0.1:  # 너무 작음
                    size_score = area_ratio / 0.1
                elif area_ratio > 0.7:  # 너무 큼
                    size_score = max(0, 1.0 - (area_ratio - 0.7) / 0.3)
                else:  # 적당한 크기 (0.1 ~ 0.7)
                    size_score = 1.0
                
                # 면적 점수 (적당한 크기일 때 높은 점수)
                area_score = min(area_ratio / 0.5, 1.0)  # 50%를 기준으로 정규화
                
                # 종합 점수 계산 (중앙 위치 40%, 적절한 크기 35%, 면적 25%)
                total_score = center_score * 0.4 + size_score * 0.35 + area_score * 0.25
                contour_info['total_score'] = total_score
                contour_info['center_score'] = center_score
                contour_info['size_score'] = size_score
                contour_info['area_score'] = area_score
                
                print(f"[DEBUG] 페이지 {page_idx + 1}, 사각형 {i+1}: 중앙={center_score:.3f}, 크기={size_score:.3f}, 면적={area_score:.3f}, 종합={total_score:.3f}")
            
            # 종합 점수가 가장 높은 사각형 선택
            rectangular_contours.sort(key=lambda x: x['total_score'], reverse=True)
            main_contour = rectangular_contours[0]
            
            print(f"[INFO] 페이지 {page_idx + 1}: 선택된 메인 사각형 면적={main_contour['area']:.0f}, 종합점수={main_contour['total_score']:.3f}")
            
            # 디버깅용: 메인 사각형 영역을 시각화하여 저장
            if enable_debug:
                save_debug_image(image_bgr, page_idx, main_contour)
            
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
            warped = cv2.warpPerspective(image_bgr, transform_matrix, (width, height))
            
            # BGR을 RGB로 변환 (PIL은 RGB 사용)
            warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            
            # PIL 이미지로 변환
            pil_warped = Image.fromarray(warped_rgb)
            
            # 추출된 이미지를 리스트에 추가
            extracted_images.append(pil_warped)
            
            print(f"[INFO] 페이지 {page_idx + 1}: 추출된 영역 크기 {width} x {height} pixels")
        
        if not extracted_images:
            print("[ERROR] 추출된 이미지가 없습니다.")
            return None
        
        # 모든 추출된 이미지를 하나의 PDF로 결합
        print(f"[INFO] {len(extracted_images)}개 페이지를 PDF로 결합 중...")
        
        # 첫 번째 이미지로 PDF 시작
        pdf_bytes_output = io.BytesIO()
        extracted_images[0].save(pdf_bytes_output, "PDF", resolution=600.0, save_all=True, append_images=extracted_images[1:])
        pdf_bytes_output.seek(0)
        pdf_content = pdf_bytes_output.getvalue()
        
        print(f"[INFO] 출력 PDF 크기: {len(pdf_content)} bytes")
        print(f"[SUCCESS] 총 {len(extracted_images)}개 페이지의 테두리 영역이 추출되어 PDF로 생성되었습니다.")
        
        return pdf_content
        
    except Exception as e:
        print(f"[ERROR] 테두리 영역 추출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None



def split_pdf_by_pages(pdf_bytes, max_pages_per_chunk=5):
    """
    PDF byte를 최대 5페이지 단위로 잘라서 byte list를 만드는 함수
    
    Args:
        pdf_bytes (bytes): PDF byte 데이터
        max_pages_per_chunk (int): 청크당 최대 페이지 수 (기본값: 5)
    
    Returns:
        list: PDF byte 데이터의 리스트
    """
    try:
        # PDF byte를 BytesIO로 변환하여 읽기
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
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
            
            # 새로운 PDF Writer 생성
            writer = PdfWriter()
            
            # 지정된 페이지 범위의 페이지들 추가
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # PDF를 byte로 변환
            chunk_bytes = io.BytesIO()
            writer.write(chunk_bytes)
            chunk_bytes.seek(0)
            
            # byte 데이터를 리스트에 추가
            pdf_chunks.append({
                "chunk_index": chunk_idx,
                "start_page": start_page + 1,
                "end_page": end_page,
                "page_count": end_page - start_page,
                "content": chunk_bytes.getvalue()
            })
            
        print(f"[INFO] 모든 청크 생성 완료. 총 {len(pdf_chunks)}개 청크")
        return pdf_chunks
        
    except Exception as e:
        print(f"[ERROR] PDF 분할 중 오류 발생: {e}")
        return []


def parse_args():
    parser = argparse.ArgumentParser(description="PDF 파일 처리 프로그램")
    parser.add_argument("--file", type=str, help="처리할 PDF 파일 경로", default="example/test_answer-2.pdf")
    parser.add_argument("--keyword", type=str, help="검색할 키워드", default="성과관리")
    parser.add_argument("--debug", action="store_true", help="디버깅 이미지 저장 여부")
    return parser.parse_args()



def main():
    args = parse_args()

    project_id = "doc-ocr-465304"

    # Processor ID as hexadecimal characters.
    # Not to be confused with the Processor Display Name.
    processor_id = "15e8648047a4a370"

    # Processor location. For example: "us" or "eu".
    location = "us"

    file_path = args.file

    # Set `api_endpoint` if you use a location other than "us".
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    # Initialize Document AI client.
    client = documentai_v1.DocumentProcessorServiceClient(client_options=opts)

    # Get the Fully-qualified Processor path.
    full_processor_name = client.processor_path(project_id, location, processor_id)

    # Get a Processor reference.
    request = documentai_v1.GetProcessorRequest(name=full_processor_name)
    processor = client.get_processor(request=request)


    with open(file_path, "rb") as f:
        pdf_content = f.read()

    pdf_chunks = split_pdf_by_pages(pdf_content)

    for chunk_idx, chunk in enumerate(pdf_chunks):
        # enable_debug=False로 설정하면 디버깅 이미지 저장 안함
        # pdf_content = extract_bordered_region_to_pdf(chunk["content"], enable_debug=args.debug)
        # pdf_chunks[chunk_idx]["content"] = pdf_content

        raw_document = documentai_v1.RawDocument(
            content=pdf_chunks[chunk_idx]["content"],
            mime_type="application/pdf",
        )
        request = documentai_v1.ProcessRequest(name=processor.name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document
        
        os.makedirs("outputs/split_text", exist_ok=True)
        with open(f"outputs/split_text/chunk_{chunk_idx}.txt", "w") as f:
            f.write(document.text)

        os.makedirs("outputs/split_pdf", exist_ok=True)
        save_path = f"outputs/split_pdf/{chunk['chunk_index']}.pdf"
        with open(save_path, "wb") as f:
            f.write(chunk["content"])


if __name__ == "__main__":
    main()