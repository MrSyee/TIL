#!/bin/sh
GOCV_VERSION=v0.31.0
# go
go get -u -d gocv.io/x/gocv@$GOCV_VERSION  # computer vision
go install golang.org/x/tools/cmd/goimports@v0.3.0  # format
go install github.com/segmentio/golines@v0.11.0  # format
go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.50.1  # lint

# opencv + gocv
case "$(uname -sr)" in
   Darwin*)
     echo 'Mac OS X'
     brew install cmake opencv@4 pkgconfig
     cd $(go env GOPATH)/pkg/mod/gocv.io/x/gocv@$GOCV_VERSION && \
        go run ./cmd/version/main.go
     ;;

   Linux*)
     echo 'Linux'
     cd $(go env GOPATH)/pkg/mod/gocv.io/x/gocv@$GOCV_VERSION && make install
     ;;

   *)
     echo 'Not Supported OS'
	 exit 1
     ;;
esac
