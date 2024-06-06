import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
from tkinter import Tk, filedialog, messagebox, Label, Button, Listbox, Scrollbar, Entry
from PIL import Image

class MangaDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Manga Downloader")

        self.label = Label(master, text="Enter the URL of the manga:")
        self.label.pack()

        self.url_entry = Entry(master, width=50)
        self.url_entry.pack()

        self.download_button = Button(master, text="Download", command=self.download_manga)
        self.download_button.pack()

        self.status_label = Label(master, text="")
        self.status_label.pack()

        self.chapters_label = Label(master, text="Chapters:")
        self.chapters_label.pack()

        self.chapter_listbox = Listbox(master, selectmode="multiple", width=50)
        self.chapter_listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(master, orient="vertical")
        self.scrollbar.config(command=self.chapter_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.chapter_listbox.config(yscrollcommand=self.scrollbar.set)

        self.get_chapters_button = Button(master, text="Get Chapters", command=self.get_chapters)
        self.get_chapters_button.pack()

        self.chapters = {}

    def get_chapters(self):
        manga_url = self.url_entry.get()
        if not manga_url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        try:
            chapters = self.chapter_links(manga_url)
            print(chapters)  # Print the chapters to debug
            self.chapters = chapters
            for chapter in chapters:
                self.chapter_listbox.insert("end", chapter)
            messagebox.showinfo("Success", "Chapters fetched successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


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

    def page_links(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        div = str(soup.find("div", {"class": "container-chapter-reader"}))
        imgs = BeautifulSoup(div, 'html.parser').find_all("img")
        page_urls = []
        for i in imgs:
            page_urls.append(i['src'])
        return page_urls

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

    def download_manga_chapter(self, name, url):
        print("Downloading " + name + " from " + url)
        pages = self.page_links(url)
        num = len(pages)
        print("Downloading " + str(num) + " pages")
        name = name.replace(':', '_')
        chapter_folder = os.path.join(DIR, name)
        if not os.path.exists(chapter_folder):
            os.makedirs(chapter_folder)
        self.download_all_images(pages, chapter_folder)
        self.convert_to_pdf(chapter_folder, name)
        print("Downloaded " + name + " successfully")

    def chapter_links(self, URL):
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html.parser')
        chapters = soup.find_all("li", class_="wp-manga-chapter")
        links = {}
        for chapter in chapters:
            chapter_name = chapter.find("a").text.strip()
            chapter_url = chapter.find("a")["href"]
            release_date = chapter.find("span", class_="chapter-release-date").text.strip()
            links[chapter_name] = {'url': chapter_url, 'release_date': release_date}
        return links

if __name__ == "__main__":
    DIR = os.getcwd()
    root = Tk()
    app = MangaDownloaderApp(root)
    root.mainloop()
