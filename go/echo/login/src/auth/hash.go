package auth

import "github.com/alexedwards/argon2id"

// HashPassword convert plaintext to argoi2id hash string
// reference: https://www.alexedwards.net/blog/how-to-hash-and-verify-passwords-with-argon2-in-go
func HashPassword(password string) (string, error) {
	// CreateHash returns a Argon2id hash of a plain-text password using the
	// provided algorithm parameters. The returned hash follows the format used
	// by the Argon2 reference C implementation and looks like this:
	// $argon2id$v=19$m=65536,t=3,p=2$c29tZXNhbHQ$RdescudvJCsgt3ub+b+dWRWJTmaaJObG

	// var DefaultParams = &Params{
	// 	Memory:      64 * 1024,
	// 	Iterations:  1,
	// 	Parallelism: 2,
	// 	SaltLength:  16,
	// 	KeyLength:   32,
	// }
	return argon2id.CreateHash(password, argon2id.DefaultParams)
}

func CheckPasswordAndHash(password, encodedHash string) (matched bool, err error) {
	// ComparePasswordAndHash performs a constant-time comparison between a plain-text password
	// and Argon2id hash, using the parameters and salt contained in the hash.
	// It returns true if they match, otherwise it returns false.
	return argon2id.ComparePasswordAndHash(password, encodedHash)
}
