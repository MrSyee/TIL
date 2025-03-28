# Vision API

FastAPI를 사용한 이미지 처리 API 서비스입니다.

서버가 실행되면 `http://localhost:8000`에서 API에 접근할 수 있습니다.

## API 엔드포인트

### 1. Health Check
- **URL**: `/healthcheck`
- **Method**: GET
- **응답**: `{"status": true}`

### 2. Noise Image 생성
- **URL**: `/image`
- **Method**: POST
- **파라미터**:
  - `size`: 이미지 크기 (양의 정수)
- **응답**: `{"message": "Image saved to output/image.png"}`
- **생성된 이미지**: `output/image.png`
