import sys
sys.path.append("..")

import tkinter
from tkinter.filedialog import askopenfilename
import customtkinter
import amazon_func_main as main
import amazon_func_s3 as s3
import amazon_func_transcribe as transcribe
import botocore.exceptions as botoe
import scrollable_label_frame as slbf

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Required variables
        self.FILE_UPLOAD = "" #default is empty

        self.title("Audio File Transcription Detector")
        self.geometry("1280x720")

        #Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Overview", 
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.upload_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Upload", 
                                                     fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), 
                                                     anchor="w", command=self.upload_button_event)
        self.upload_button.grid(row=2, column=0, sticky="ew")

        self.list_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Audio List", 
                                                     fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), 
                                                     anchor="w", command=self.list_button_event)
        self.list_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["System", "Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        #Create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_label = customtkinter.CTkLabel(self.home_frame, text="Welcome Home!",
                                                       font=customtkinter.CTkFont(size=20, weight="bold"))
        self.home_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # create upload frame
        self.upload_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.upload_frame.grid_columnconfigure(0, weight=1)

        self.upload_title = customtkinter.CTkLabel(self.upload_frame, text="Upload Page",
                                                   font=customtkinter.CTkFont(size=20, weight="bold"))
        self.upload_title.grid(row=0, column=0, padx=20, pady=20)

        self.choose_file_button = customtkinter.CTkButton(self.upload_frame, corner_radius=0, height=20, border_spacing=5, text="Choose File",
                                                          command=self.choose_file)
        self.choose_file_button.grid(row=1, column=0, padx=20, pady=10)
   
        self.selected_file_label = customtkinter.CTkLabel(self.upload_frame, text="",
                                                          font=customtkinter.CTkFont(size=15, weight="normal"))
        if(self.FILE_UPLOAD == ""):
            self.selected_file_label.configure(text="(File not yet selected)")
        else:
            selected_file_text = "Selected File: " + self.FILE_UPLOAD
            self.selected_file_label.configure(text=selected_file_text)
        self.selected_file_label.grid(row=2, column=0, padx=20, pady=20)

        self.upload_file_button = customtkinter.CTkButton(self.upload_frame, corner_radius=0, height=20, border_spacing=5, text="Upload Audio File",
                                                          command=self.upload_file)
        self.upload_file_button.grid(row=3, column=0, padx=20, pady=20)

        self.upload_status_msg = customtkinter.CTkLabel(self.upload_frame, text="",
                                                   font=customtkinter.CTkFont(size=15, weight="bold"))
        self.upload_status_msg.grid(row=4, column=0, padx=20, pady=20)

        # create list frame
        self.list_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        self.list_title = customtkinter.CTkLabel(self.list_frame, text="Audio Files",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.list_title.grid(row=0, column=0, padx=20, pady=20)

        self.column_filename = customtkinter.CTkLabel(self.list_frame, text="File Name", compound="left", padx=5, anchor="w", text_color="grey")
        self.column_filename.grid(row=1, column=0, pady=(0, 10), sticky="w")

        self.scrollable_frame = slbf.ScrollableLabelButtonFrame(master=self.list_frame, height=500, command=None, corner_radius=0)
        self.scrollable_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        #Select default frame
        self.select_frame_by_name("home")

        
    def select_frame_by_name(self, name):
        #Set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.upload_button.configure(fg_color=("gray75", "gray25") if name == "upload" else "transparent")
        self.list_button.configure(fg_color=("gray75", "gray25") if name == "list" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "upload":
            self.upload_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.upload_frame.grid_forget()
        if name == "list":
            self.list_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.scrollable_frame.remove_all_items()
            self.list_frame.grid_forget()

    
    def home_button_event(self):
        self.select_frame_by_name("home")

    def upload_button_event(self):
        self.upload_status_msg.configure(text="")
        self.select_frame_by_name("upload")
    
    def list_button_event(self):
        self.scrollable_frame.remove_all_items()
        list_of_audio_files = s3.list_objects(main.s3_uri_bucket, main.s3_client)
        for fileName in list_of_audio_files:
            self.scrollable_frame.add_item(fileName, image=None)
        self.select_frame_by_name("list")
    
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def choose_file(self):
        self.FILE_UPLOAD = askopenfilename()
        selected_file_text = "Selected File: " + self.FILE_UPLOAD
        self.selected_file_label.configure(text=selected_file_text)
        self.upload_status_msg.configure(text="")

    def upload_file(self):
        try:
            print(self.FILE_UPLOAD)
            list_of_files = s3.list_objects(main.s3_uri_bucket, main.s3_client)
            if self.FILE_UPLOAD.split("/")[-1] in list_of_files:
                self.upload_status_msg.configure(text="File with same name already exists!")
            else:
                s3.upload_file(self.FILE_UPLOAD, main.s3_client, main.s3_uri_bucket, self.FILE_UPLOAD.split("/")[-1])
        except botoe.ClientError:
            self.upload_status_msg.configure(text="Upload failed!")
        except FileNotFoundError:
            self.upload_status_msg.configure(text="File does not exist!")
        else:
            if not self.FILE_UPLOAD.split("/")[-1] in list_of_files:
                self.FILE_UPLOAD = ""
                self.selected_file_label.configure(text="(File not yet selected)")
                self.upload_status_msg.configure(text="Upload Successful!")

    
if __name__ == "__main__":
        app = App()
        app.change_appearance_mode_event("System")
        app.mainloop()
