from tkinter import *
from tkinter import ttk
#import youtube_dl
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
import threading

class MainWindow():
	def __init__(self,root):	
		
		self.onetimeclick = 0
		self.songentry = ""

		#Window Information
		self.root = root
		self.root.title("YT-DL GUI")
		self.root.resizable(False, False)
		
		self.w_frame = Frame(self.root)
		self.w_frame.pack()

		self.l = Label(self.w_frame, text="").pack()
		self.l = Label(self.w_frame, text="Enter Title(s) (Each Separated By A New Line)").pack()

		self.l = Label(self.w_frame, text="").pack()

		self.t_frame= Frame(self.w_frame)
		self.scroll_y = Scrollbar(self.t_frame, orient=VERTICAL)
		self.scroll_x = Scrollbar(self.t_frame, orient=HORIZONTAL)
		self.t = Text(self.t_frame, wrap=NONE, width=55, height=16, font=("Helvetica",16), yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
		self.t.insert(END,"""Artist And Album Tags Can Be Inserted Via '//' and '/' Respectively\nFor Example:\n//Fuegosan\n/Singles\nFuegosan - System\n\n//Various Artists\nKelpy - Memory Card\nSome Guy - Mixed Fried Rice\n\nAudio Will Be Assigned The Default Values If No Tags Are Specified\n//defaults Could Also Be Used To Apply Default Tags\n\nTo Search For Something Specific Wrap The Word In Quotation Marks\nFor Example:\nFuegosan - "mood" """)
		
		self.t.config(state=DISABLED)
		self.t.bind("<Button-1>",self.clearTextBoxByClick)
		self.scroll_y.config(command = self.t.yview ) 
		self.scroll_x.config(command = self.t.xview ) 

		self.t_frame.pack()
		self.scroll_y.pack(side = RIGHT, fill=Y)
		self.scroll_x.pack(side = BOTTOM, fill=X)
		self.t.pack()

		self.l = Label(self.w_frame, text="").pack()
		self.btn = Button(self.w_frame,text="Download", state=DISABLED, command=lambda:threading.Thread(target = self.getSongs).start())
		self.btn.pack()

		self.l = Label(self.w_frame, text="").pack()
		self.pbar = ttk.Progressbar(self.w_frame, orient=HORIZONTAL, length=300, mode='determinate')
		self.pbar.pack()

		self.statuslabel = Label(self.w_frame)
		self.statuslabel.pack()
		self.l = Label(self.w_frame, text="").pack()

	def getSongs(self):
		self.btn.config(state=DISABLED)
		self.t.config(state=DISABLED)
		self.statuslabel.config(text="Preparing...")
		songlist = self.t.get(1.0,'end-1c').split("\n")
		songcount = 1
		artist = "Various"
		album = "Multiple"
		for song in songlist:
			song = song.strip()
			self.songentry = song
			if song != "":
				if song.lower() == "//defaults":
					artist = "Various"
					album = "Multiple"
				elif song[0:2] == "//":
					artist = song.replace("//","")
					album = "Multiple"								
				elif song[0] == "/":
					album = song.replace("/","")					
				else:
					try:
						info = YoutubeDL({}).extract_info('ytsearch:'+song, download=False, ie_key='YoutubeSearch')
						self.statuslabel.config(text=f"Downloading {song}")
						ydl_opts = {
							'format': 'bestaudio/best',
							'writethumbnail': True,
							'outtmpl': 'downloaded/'+artist+'/'+album+'/%(title)s.%(ext)s',
							'postprocessors': [
								{'key': 'FFmpegExtractAudio',
								'preferredcodec': 'mp3',
								'preferredquality': '192',}, 
								{'key': 'EmbedThumbnail',}
								],
							'progress_hooks': [self.progressBar],
						}
						with YoutubeDL(ydl_opts) as ydl:
							ydl.cache.remove()
							info_dict = ydl.extract_info(info['entries'][0]['id'], download=False)
							ydl.download([info['entries'][0]['id']])
							filename = ydl.prepare_filename(info_dict)
						filename = filename.replace(".webm",".mp3")
						filename = filename.replace(".m4a",".mp3")
						title = filename.replace(".mp3","")
						title = title.replace("downloaded/"+artist+"/"+album+"/","")
						self.addMetadata(filename,title,artist,album)
						songcount = songcount+1

					except Exception:
						self.statuslabel.config(text=f"Error: Couldn't Download Song {song}")
						self.t.insert(str(songcount)+".0","Failpoint --> ")
						self.btn.config(state=NORMAL)
						self.t.config(state=NORMAL)
						return
			else:
				continue

		self.statuslabel.config(text=f"{str(songcount-1)} File(s) Downloaded")
		self.btn.config(state=NORMAL)
		self.t.config(state=NORMAL)

	def addMetadata(self,filename,title,artist,album):
		audio = EasyID3(filename)
		audio['title'] = title
		audio['artist'] = artist
		audio['album'] = album
		audio.save()

	def progressBar(self,d):
		if d['status'] == 'downloading':
			currentpercent = d['_percent_str']
			currentpercent = currentpercent.replace('%','')
			self.pbar['value'] = currentpercent
			self.root.update_idletasks()
		elif d['status'] == 'finished':
			self.statuslabel.config(text=f"Converting {self.songentry} to .mp3")
			self.pbar['value'] = 0

	def clearTextBoxByClick(self,event):
		if self.onetimeclick == 0:
			self.t.config(state=NORMAL)
			self.t.delete(1.0,END)
			self.onetimeclick = 1
			self.btn.config(state=NORMAL)
		 

def main(): 
	#creates main tkinter window
	root = Tk()
	app = MainWindow(root)
	mainloop()

if __name__ == '__main__':
	main()
