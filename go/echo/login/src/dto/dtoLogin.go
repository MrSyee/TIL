package dto

type LoginReq struct {
	Username string `json:"username" form:"username"`
	Password string `json:"password" form:"password"`
}

type LoginResp struct {
	Token string `json:"token" form:"token"`
}
