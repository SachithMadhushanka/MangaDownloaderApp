# MangaDownloaderApp

## Overview

MangaDownloaderApp is a Python-based desktop application designed to download manga chapters from a given URL. The application allows users to fetch available chapters, select specific chapters to download, and save the manga chapters as PDF files.

## Features

- Fetch available manga chapters from a given URL.
- Select multiple chapters to download.
- Download all pages of the selected chapters.
- Convert downloaded images to PDF format.
- User-friendly interface with Tkinter.

## Requirements

- Python 3.x
- Requests
- BeautifulSoup4
- Pillow
- Threading
- Tkinter

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/manga-downloader-app.git
   cd manga-downloader-app
   ```

2. **Install the required Python packages:**
   ```bash
   pip install requests beautifulsoup4 pillow
   ```

## Usage

1. **Run the application:**
   ```bash
   python manga_downloader_app.py
   ```

2. **Use the application:**
   - Enter the URL of the manga in the input field.
   - Click the "Get Chapters" button to fetch available chapters.
   - Select the chapters you want to download from the list.
   - Click the "Download" button to start the download and conversion process.
   - The selected chapters will be downloaded as images and saved as PDF files.

## Script Explanation

### Importing Libraries
```python
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
from tkinter import Tk, filedialog, messagebox, Label, Button, Listbox, Scrollbar, Entry
from PIL import Image
```
- **requests**: For making HTTP requests to fetch web content.
- **BeautifulSoup**: For parsing HTML content.
- **os**: For file and directory operations.
- **urllib.parse**: For URL parsing.
- **threading**: For handling concurrent downloads.
- **tkinter**: For creating the graphical user interface.
- **Pillow**: For handling image processing and conversion to PDF.

### MangaDownloaderApp Class
#### Initialization
```python
class MangaDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Manga Downloader")
        ...
```
- Initializes the main window and sets up the user interface.

#### Fetching Chapters
```python
def get_chapters(self):
    manga_url = self.url_entry.get()
    if not manga_url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    try:
        chapters = self.chapter_links(manga_url)
        print(chapters)
        self.chapters = chapters
        for chapter in chapters:
            self.chapter_listbox.insert("end", chapter)
        messagebox.showinfo("Success", "Chapters fetched successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
```
- Fetches available chapters from the provided URL and displays them in the listbox.

#### Downloading Manga Chapters
```python
def download_manga(self):
    selected_chapters = [self.chapter_listbox.get(idx) for idx in self.chapter_listbox.curselection()]
    if not selected_chapters:
        messagebox.showerror("Error", "Please select chapters to download.")
        return

    manga_url = self.url_entry.get()
    if not manga_url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    try:
        for chapter in selected_chapters:
            self.download_manga_chapter(chapter, self.chapters[chapter])
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during download: {str(e)}")
```
- Downloads the selected chapters, saves images, and converts them to PDF.

#### Downloading Pages
```python
def page_links(self, url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    div = str(soup.find("div", {"class": "container-chapter-reader"}))
    imgs = BeautifulSoup(div, 'html.parser').find_all("img")
    page_urls = []
    for i in imgs:
        page_urls.append(i['src'])
    return page_urls
```
- Fetches image URLs from the chapter page.

#### Downloading Images
```python
def download_all_images(self, urls, chapter_folder):
    def download(name, url):
        domain = urllib.parse.urlparse(url).netloc
        HEADERS = {
            'Accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
            'Host': domain, 'Accept-Language': 'en-ca', 'Referer': 'https://manganelo.com/',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=HEADERS, stream=True)
        with open(os.path.join(chapter_folder, name), 'wb') as f:
            f.write(r.content)

    threads = []
    for idx, url in enumerate(urls):
        t = threading.Thread(target=download, args=(f"image_{idx+1}.jpg", url))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()
```
- Downloads all images from the fetched URLs using threading for faster performance.

#### Converting Images to PDF
```python
def convert_to_pdf(self, chapter_folder, chapter_name):
    images = []
    for root, dirs, files in os.walk(chapter_folder):
        for file in files:
            if file.endswith(('jpg', 'jpeg', 'png', 'gif')):
                image_path = os.path.join(root, file)
                image = Image.open(image_path)
                images.append(image)

    pdf_filepath = os.path.join(chapter_folder, f"{chapter_name}.pdf")
    try:
        images[0].save(pdf_filepath, save_all=True, append_images=images[1:])
        messagebox.showinfo("Conversion Complete", "Images converted to PDF successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
```
- Converts the downloaded images into a single PDF file.

### Main Loop
```python
if __name__ == "__main__":
    DIR = os.getcwd()
    root = Tk()
    app = MangaDownloaderApp(root)
    root.mainloop()
```
- Creates the main application window and starts the Tkinter event loop.

## License

This project is licensed under the MIT License.
