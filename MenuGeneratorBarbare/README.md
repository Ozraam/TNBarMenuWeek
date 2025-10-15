docker build -t combar:v0.1 .
docker run -v ./build:/app/build combar:v0.1

The image generator now relies on Playwright. After installing the Python dependencies run:

```
playwright install chromium
```

To update the main logo displayed on the generated menus, upload a PNG image to the backend:

> **Note:** Only PNG files are accepted for upload.
```
curl -X POST \
	-F "imageFile=@/path/to/logo.png" \
	-F "name=nouveau-logo" \
	http://localhost:5000/logo
```

The server stores the file in `MenuGeneratorBarbare/logos/` and updates `style.json` so the generator picks it up automatically.