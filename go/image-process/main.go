/*
Image IO example using image and gocv module.
Read file using image module.
Convert to jpeg byte.
Decode CV mat.
*/

package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"image"
	"image/jpeg"
	"os"

	"gocv.io/x/gocv"
)

func readImageFromFilePath(path string) (image.Image, error) {
	var img image.Image

	f, err := os.Open(path)
	fmt.Printf("OS OPEN: %v", f)
	if err != nil {
		return img, err
	}
	defer f.Close()

	image, _, err := image.Decode(f)
	return image, err
}

func main() {
	// Args parser
	imageFilePath := flag.String("image", "sample/sample_image.jpg", "The image path")
	flag.Parse()

	// Read image
	image, err := readImageFromFilePath(*imageFilePath)
	if err != nil {
		fmt.Println("failed to read image from file path: %w", err)
	}

	// Jpg encode
	f, err := os.Create("sample/output.jpg")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	if err = jpeg.Encode(f, image, nil); err != nil {
		fmt.Println("failed to encode: %w", err)
	}

	// Show using cv
	var jpgByte bytes.Buffer
	w := bufio.NewWriter(&jpgByte)
	err = jpeg.Encode(w, image, nil)
	if err != nil {
		fmt.Println("failed to encode: %w", err)
	}

	cvImage, err := gocv.IMDecode(jpgByte.Bytes(), gocv.IMReadGrayScale)
	if err != nil {
		fmt.Println("Failed to decode jpeg byte: %w", err)
	}
	defer cvImage.Close()

	window := gocv.NewWindow("Result")
	defer window.Close()
	window.IMShow(cvImage)
	window.WaitKey(0)
}
