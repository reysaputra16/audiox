import customtkinter
import os
from PIL import Image

class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.text_list = []
        self.label_list = []
        self.button_remove_list = []
        self.button_transcribe_list = []

    def add_item(self, item, image=None):
        label = customtkinter.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button_transcribe = customtkinter.CTkButton(self, text="Transcribe", width=100, height=24)
        button_remove = customtkinter.CTkButton(self, text="Remove", width=100, height=24)
        #button_remove = customtkinter.CTkButton(self, text="Remove", width=100, height=24, text_color="white", bg_color="red")
        if self.command is not None:
            button_remove.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button_transcribe.grid(row=len(self.button_transcribe_list), column=1, pady=(0, 10), padx=5)
        button_remove.grid(row=len(self.button_remove_list), column=2, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_transcribe_list.append(button_transcribe)
        self.button_remove_list.append(button_remove)
        self.text_list.append(item)

    def remove_item(self, item):
        for label, button_transcribe, button_remove in zip(self.label_list, self.button_transcribe_list, self.button_remove_list):
            if item == label.cget("text"):
                label.destroy()
                button_transcribe.destroy()
                button_remove.destroy()
                self.label_list.remove(label)
                self.button_transcribe_list.remove(button_transcribe)
                self.button_remove_list.remove(button_remove)
                self.text_list.remove(item)
                return
            
    def remove_all_items(self):
        for text in self.text_list:
            self.remove_item(text)