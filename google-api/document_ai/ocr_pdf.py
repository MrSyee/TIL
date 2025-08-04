import argparse
import os

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1
from pdf_controller import find_keyword_positions, add_bounding_box_to_pdf, print_text_positions

from dotenv import load_dotenv

load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(description="PDF 파일 처리 프로그램")
    parser.add_argument("--file", type=str, help="처리할 PDF 파일 경로", default="example/test_answer-2.pdf")
    parser.add_argument("--keyword", type=str, help="검색할 키워드", default="성과관리")
    return parser.parse_args()

def main():
    args = parse_args()
    # TODO(developer): Create a processor of type "OCR_PROCESSOR".

    # TODO(developer): Update and uncomment these variables before running the sample.
    project_id = "doc-ocr-465304"

    # Processor ID as hexadecimal characters.
    # Not to be confused with the Processor Display Name.
    processor_id = "15e8648047a4a370"

    # Processor location. For example: "us" or "eu".
    location = "us"

    # Path for file to process.
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

    # `processor.name` is the full resource name of the processor.
    # For example: `projects/{project_id}/locations/{location}/processors/{processor_id}`
    print(f"Processor Name: {processor.name}")

    # Read the file into memory.
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load binary data.
    # For supported MIME types, refer to https://cloud.google.com/document-ai/docs/file-types
    raw_document = documentai_v1.RawDocument(
        content=image_content,
        mime_type="application/pdf",
    )

    # Send a request and get the processed document.
    request = documentai_v1.ProcessRequest(name=processor.name, raw_document=raw_document)
    result = client.process_document(request=request)
    document = result.document

    # Read the text recognition output from the processor.
    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    print("The document contains the following text:")
    print(document.text)

    # Save the text to a file
    with open("outputs/output.txt", "w") as f:
        f.write(document.text)


    search_text = args.keyword
    positions = find_keyword_positions(document, search_text)

    # 찾은 텍스트 위치 정보 출력
    print_text_positions(positions)

    # 바운딩 박스 추가
    output_pdf_path = f"outputs/{search_text}.pdf"
    if positions:
        add_bounding_box_to_pdf(file_path, output_pdf_path, positions)
    else:
        print(f"'{search_text}' 텍스트를 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
