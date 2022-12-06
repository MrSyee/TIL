package handler

import "mime/multipart"

type sumRequest struct {
	InputX int `json:"inputX" form:"inputX" xml:"inputX"`
	InputY int `json:"inputY" form:"inputY" xml:"inputY"`
}

type sumResponse struct {
	Sum int `json:"sum" form:"sum" xml:"sum"`
}

type fileRequest struct {
	FileName string                `json:"filename" form:"filename" xml:"filename"`
	File     *multipart.FileHeader `json:"file" form:"file" xml:"file"`
}

type fileResponse struct {
	Success bool `json:"file" form:"file" xml:"file"`
}
