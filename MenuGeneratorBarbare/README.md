docker build -t combar:v0.1 .
docker run -v ./build:/app/build combar:v0.1

The image generator now relies on Playwright. After installing the Python dependencies run:

```
playwright install chromium
```