# -*- coding: utf-8 -*-

import os
import re
import copy
import json
import base64
import random
import shutil
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from CTkListbox import CTkListbox
from bs4 import BeautifulSoup, Comment
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageDraw, ImageFont
import webbrowser

ctk.set_default_color_theme('green')  # Themes: "blue" (standard), "green", "dark-blue"
LARGEFONT = ('Helvetica', 14)

up_maroon = '#850038'
up_maroon_l = '#f60068'
up_maroon_d = '#5d0027'

forest_green = '#0e6021'
forest_green_l = '#1dc945'
forest_green_d = '#0a4317'

# yellow_gold = '#ffac0d'

class OCPWizApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        ctk.set_appearance_mode('Light')
        self.geometry('800x600')
        self.title('OCPWiz')
        self.resizable(False,False)

        self.frames = {}

        self.faculty = ''
        self.course_no = ''
        self.course_title = ''
        self.num_topics = -1
        self.course_intro = []

        self.course_guide_dir = ''
        self.resources_dir = []
        self.topics_dir = {}
        self.questions = {}

        sidebar_frame=ctk.CTkFrame(self, width=170,fg_color=up_maroon)
        sidebar_frame.pack(side='left', fill='y')
        sidebar_frame.grid_propagate(False)
        self.frames[ctk.CTkFrame]=sidebar_frame
        
        

        self.sidebar_head = ctk.CTkFrame(sidebar_frame,width=165,height=120,fg_color=up_maroon)
        self.sidebar_head.grid(row=0, column=0, columnspan=1, )
        self.sidebar_head.pack_propagate(False)

        with Image.open(os.path.join(os.path.dirname(__file__),'files/', 'course/', 'img/', 'upou.png')) as img:
            width, height = img.size
            width_new=int(width/6)
            height_new=int(height/6)
            my_img = ctk.CTkImage(light_image=img,
                                size=(width_new,height_new))
            img_label = ctk.CTkLabel(self.sidebar_head, image=my_img, text='')
            img_label.pack(pady=(30,0))
        
        #COURSE INFO BTN------------------------------------------------------------------------------------------------------------------------------------
        self.course_info_btn = ctk.CTkButton(sidebar_frame,text="Course Info",width=165,height=70,font=LARGEFONT,anchor="w",fg_color=up_maroon, hover_color=up_maroon_d,
                                             command=lambda: self.indicate(self.course_info_btn, CourseInfoPage,))
        self.course_info_btn.grid(row=1, column=0, columnspan=1)

        self.resources_btn = ctk.CTkButton(sidebar_frame,text='',width=165,height=70,font=LARGEFONT,anchor="w",state=ctk.DISABLED,fg_color=up_maroon,hover_color=up_maroon_d,
                                           command=lambda: [
                                               self.refresh_resourcesPage(),
                                               self.indicate(self.resources_btn, ResourcesPage,)
                                               ])
        self.resources_btn.grid(row=2, column=0, columnspan=1,sticky=ctk.E + ctk.W)

        self.upload_topics_btn = ctk.CTkButton(sidebar_frame,text='',width=165,height=70,font=LARGEFONT,anchor="w",state=ctk.DISABLED,fg_color=up_maroon,hover_color=up_maroon_d,
                                               command=lambda: [
                                                   self.refresh_uploadTopicsPage(),
                                                   self.indicate(self.upload_topics_btn, UploadTopicsPage)
                                                ])
        self.upload_topics_btn.grid(row=3, column=0, columnspan=1)

        self.create_quiz_btn = ctk.CTkButton(sidebar_frame,text='',width=165,height=70,font=LARGEFONT,anchor="w",state=ctk.DISABLED,fg_color=up_maroon,hover_color=up_maroon_d,
                                             command=lambda: [
                                                   self.refresh_createQuizPage(),
                                                   self.indicate(self.create_quiz_btn, CreateQuizPage)
                                            ])
        self.create_quiz_btn.grid(row=4, column=0, columnspan=1)

        self.create_ocp_btn = ctk.CTkButton(sidebar_frame,text='',width=165,height=70,font=LARGEFONT,anchor="w",state=ctk.DISABLED,fg_color=up_maroon, hover_color=up_maroon_d,
                                            command=lambda: [self.check_ocp()])
        self.create_ocp_btn.grid(row=5, column=0, columnspan=1)

        self.switch_var = ctk.StringVar(value='off')
        self.dark_mode = ctk.CTkSwitch(sidebar_frame, text='Dark Mode', command=self.DarkLight, variable=self.switch_var, onvalue='on', offvalue='off', text_color='white')
        self.dark_mode.grid(row=6, column=0, columnspan=1)

        header = ctk.CTkFrame(self,height=105)
        header.pack(side='top',fill='x')
        header.grid_propagate(False)
        header.grid_columnconfigure(0,weight=1)
        header.grid_columnconfigure(2,weight=4)
        header.grid_rowconfigure(0,weight=1)
        header.grid_rowconfigure(3,weight=1)

        self.header_title = ctk.CTkLabel(header, text='', font=('Helvetica', 30))
        self.header_title.grid(row=1, column=1,sticky=ctk.W)
        self.header_subtitle = ctk.CTkLabel(header, text='', font=('Helvetica', 15))
        self.header_subtitle.grid(row=2, column=1,sticky=ctk.W)

        container = ctk.CTkFrame(self, fg_color='red')
        container.pack(side='top', fill='both',expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight = 1)

        for F in (
                  CourseInfoPage,
                  ResourcesPage,
                  DelResourcesPage,
                  UploadTopicsPage,
                  CreateQuizPage,
                  CreateOCPPage
                  ):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.indicate(self.course_info_btn, CourseInfoPage)

    def DarkLight(self):
        print("switch toggled, current value:", self.switch_var.get())
        if self.switch_var.get() == 'off':
            ctk.set_appearance_mode('Light')  # Modes: "System" (standard), "Dark", "Light"
        else:
            ctk.set_appearance_mode('Dark')
    #SAVE DETAILS ------------------------------
    def save_course_info(self, faculty, course_no, course_title, num_topics, course_intro):
        if self.num_topics == -1 or self.num_topics == num_topics:
            self.set_details(faculty, course_no, course_title, num_topics, course_intro)
            if bool(self.topics_dir) == False and bool(self.questions) == False:
                self.update_num_topics()
            self.enable_buttons()
        elif self.num_topics != num_topics:
            msg_box = CTkMessagebox(title='Warning', message='Changing the number of topics will remove all uploaded PDFs and saved quizzes. Continue?',
                                icon='warning', option_1='Yes', option_2='No')
            if msg_box.get()=='Yes':
                self.set_details(faculty, course_no, course_title, num_topics, course_intro)
                self.topics_dir.clear()
                self.questions.clear()
                self.update_num_topics()
                self.enable_buttons()

    def set_details(self,faculty, course_no, course_title, num_topics, course_intro):
        self.faculty = faculty
        self.course_no = course_no
        self.course_title = course_title
        self.num_topics = num_topics
        self.course_intro = course_intro
    
    def update_num_topics(self):
        temp = []
        for x in range(self.num_topics):
            temp.append(x+1)

        self.topics_dir = dict.fromkeys(temp)
        self.questions = dict.fromkeys(temp)
        self.questions["final"]=None

    def save_course_guide(self, course_guide):
        self.course_guide_dir = course_guide

    def save_resources_dir(self, source, value):
        if value == "Folder":
            if [source, 0] not in self.resources_dir:
                self.resources_dir.append([source, 0])
        elif value == "File":
            if [source, 1] not in self.resources_dir:
                self.resources_dir.append([source, 1])
        elif value == "Exist":
            self.resources_dir = source

        self.resources_dir.sort(key=lambda x: (x[1], x[0]))
        
    def delete_resource_dir(self, value):
        # print(self.resources_dir[value])
        del self.resources_dir[value]

    def save_topics_dir(self, topics_dir):
        self.topics_dir = topics_dir

    def save_questions(self, questions):
        self.questions = questions
    
    #GETTERS----------------------------------------------
    def get_faculty(self):
        return self.faculty

    def get_course_no(self):
        return self.course_no
    
    def get_course_title(self):
        return self.course_title
    
    def get_course_intro(self):
        return self.course_intro

    def get_course_guide_dir(self):
        return self.course_guide_dir

    def get_resources_dir(self):
        return self.resources_dir
    
    def get_num_topics(self):
        return self.num_topics
    
    def get_topics_dir(self):
        return self.topics_dir
    
    def get_questions(self):
        return self.questions
    
    #REFRESH PAGES----------------------------------------
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def indicate(self, btn, page):
        self.not_indicate()
        btn.configure(fg_color=up_maroon_l)
        self.change_header(page)
        # if page == 'ResourcesPage':
        #     self.refresh_resourcesPage()
        self.show_frame(page)
        

    def change_header(self, page):
        if page == CourseInfoPage:
            self.header_title.configure(text='Course Information')
            self.header_subtitle.configure(text='Provide Details for the Course')
        elif page == ResourcesPage:
            self.header_title.configure(text='Course Resources')
            self.header_subtitle.configure(text='Upload, View, and Delete Course Materials')
        elif page == UploadTopicsPage:
            self.header_title.configure(text='Upload Topics')
            self.header_subtitle.configure(text='Upload PDFs for Each Topic')
        elif page == CreateQuizPage:
            self.header_title.configure(text='Create Quiz')
            self.header_subtitle.configure(text='Upload Quiz in GIFT Format')
        elif page == CreateOCPPage:
            self.header_title.configure(text='Offline Course Package')
            self.header_subtitle.configure(text='Review and Finalize Course Package Details')
        elif page == DelResourcesPage:
            self.header_title.configure(text='Delete Resources')
            self.header_subtitle.configure(text='Manage Uploaded Course Materials')
    
    def not_indicate(self):
        self.course_info_btn.configure(fg_color=up_maroon)
        self.resources_btn.configure(fg_color=up_maroon)
        self.upload_topics_btn.configure(fg_color=up_maroon)
        self.create_quiz_btn.configure(fg_color=up_maroon)
        self.create_ocp_btn.configure(fg_color=up_maroon)

    def enable_buttons(self):
        self.resources_btn.configure(state=ctk.NORMAL, text='Manage Resources')
        self.upload_topics_btn.configure(state=ctk.NORMAL, text='Upload Topics')
        self.create_quiz_btn.configure(state=ctk.NORMAL, text="Create Quiz")
        self.create_ocp_btn.configure(state=ctk.NORMAL,text='Create Offline Package')

    def refresh_resourcesPage(self):
        self.frames[ResourcesPage].update()

    def refresh_delResourcePage(self):
        self.frames[DelResourcesPage].update_lb()
    
    def refresh_uploadTopicsPage(self):
        self.frames[UploadTopicsPage].update_btns()

    def refresh_createQuizPage(self):
        self.frames[CreateQuizPage].update_btns()

    def refresh_createOCPPage(self):
        self.frames[CreateOCPPage].update_details()

    #TEST------------------------
    def check_ocp(self):
        if self.course_guide_dir == '':
            msg_box = CTkMessagebox(title="Error", message="No Course Guide Uploaded", icon="cancel", button_color=forest_green, button_hover_color=forest_green_d,)
            return
        
        no_topics = False
        no_topic_pdf = 'No Uploaded PDF for Topics: '
        for x in self.topics_dir.keys():
            if self.topics_dir[x] == None:
                no_topic_pdf += f'{x}, '
                no_topics = True

        if no_topics:
            msg_box = CTkMessagebox(title='Error', message=f'{no_topic_pdf[:-2]}', icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)
            return
        
        self.refresh_createOCPPage()
        self.indicate(self.create_ocp_btn, CreateOCPPage)
            
    def test(self):
        pass

    # CREATE OCP-------------------------------------------------------------
    def create_ocp(self):
        try:
            copy_dir=""
            curr_dir = os.path.join('Interactive Offline Course/', f'{self.course_no}')
            path = '{}'.format(filedialog.askdirectory(title='Select Folder'))
            if path:
                copy_dir = path
            else:
                msg_box = CTkMessagebox(title='Error', message='No folder selected',icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)
            shutil.copytree(os.path.join(os.path.dirname(__file__),'files'),os.path.join(os.path.dirname(__file__),'Interactive Offline Course'))
            os.rename(os.path.join(os.path.dirname(__file__),'Interactive Offline Course/', 'course'), os.path.join(os.path.dirname(__file__),curr_dir))
            #introduction.html ---------------------------------------------------------------------------------------------------------------------
            if self.course_guide_dir:
                    target = os.path.join(os.path.dirname(__file__),f'{curr_dir}/','modules')
                    dir_parts = list(os.path.split(self.course_guide_dir))
                    target_dir = os.path.join(target, 'CourseGuide.pdf')
                    shutil.copy2(self.course_guide_dir, target_dir)
            
            soup_new = self.createSoup(os.path.join(os.path.dirname(__file__), f'{curr_dir}/','introduction.html'))
            h2 = soup_new.h2
            h2.string = self.course_no + ' - ' + self.course_title
            if self.course_intro:
                for p in soup_new.find_all('p', class_=False):
                    p.decompose()
                p_tag = soup_new.new_tag('p')
                p_tag.string = self.course_intro[0]
                soup_new.hr.insert_after(p_tag)
                for course_intro_word in self.course_intro[1:]:
                    next_p = soup_new.find_all('p', class_=False)[-1]
                    p_tag = soup_new.new_tag('p')
                    p_tag.string = course_intro_word
                    next_p.insert_after(p_tag)

            self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','introduction.html'), 
                    soup_new.prettify(formatter="html"))
            
            #course.html ---------------------------------------------------------------------------------------------------------------------
            soup_new = self.createSoup(os.path.join(os.path.dirname(__file__),'template/','HTML/','course_template.html'))
            to_append = []
            new_title=soup_new.new_tag('title')
            new_title.string=f'{self.course_no} Interactive Offline Course'
            soup_new.html.head.title.replace_with(new_title)
            for x in range(int(self.num_topics)):
                self.create_li_tag(to_append,soup_new, x+1, f"Topic {x+1}",)
            if self.questions['final'] != None:
                self.create_li_tag(to_append,soup_new, self.num_topics+1, "Final Exam")
            for x in to_append:
                ul_tag = soup_new.find("ul")
                ul_tag.append(x)

            self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','course.html'), 
                    soup_new.prettify(formatter="html"))
            
            #profile.html ---------------------------------------------------------------------------------------------------------------------
            soup_new = self.createSoup(os.path.join(
                        os.path.dirname(__file__),f'template/','HTML/','profile_template.html'))
                    
            first_link = soup_new.find('p', class_='faculty')
            first_link.string=self.faculty
            
            self.tag_replace(soup_new, "#Course#", self.course_no + ' - ' + self.course_title)
        
            self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','profile.html'), 
                soup_new.prettify(formatter="html"))
            
            #register.html ---------------------------------------------------------------------------------------------------------------------
            soup_new = self.createSoup(os.path.join(
                        os.path.dirname(__file__),f'template/','HTML/','register_template.html'))
                    
            self.tag_replace(soup_new,"#Course Name#", self.course_no)
            self.tag_replace(soup_new,"#Course Title#", self.course_title)
            
            self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','register.html'), 
                soup_new.prettify(formatter="html"))
            
            #resources.html ---------------------------------------------------------------------------------------------------------------------
            if self.resources_dir:
                # print(self.resources_dir)
                temp = []
                for src in self.resources_dir:
                    resourceName = src[0].split('/')[-1]
                    # print(resourceName)
                    dir = os.path.join(os.path.dirname(__file__),f'{curr_dir}/','resources/', f'{resourceName}')
                    if src[1] == 0:
                        shutil.copytree(src[0], dir)
                        hasPDF = False
                        for root, dirs, files in os.walk(dir):
                            for file in files:
                                if file.endswith(".pdf"):
                                    hasPDF = True
                        li_tag = soup_new.new_tag("li")
                        a_tag = ""
                        if hasPDF == True:
                            a_tag = soup_new.new_tag("a", href=f"resources/{resourceName}", id="manual")
                        else:
                            a_tag = soup_new.new_tag("a", href=f"resources/{resourceName}")
                        a_tag.string = resourceName
                        li_tag.append(a_tag)
                        temp.append(li_tag)
                    else:
                        shutil.copy(src[0], dir)
                        li_tag = soup_new.new_tag("li")
                        a_tag = soup_new.new_tag("a", href=F"resources/{resourceName}")
                        a_tag.string = resourceName
                        li_tag.append(a_tag)
                        temp.append(li_tag)

                soup_new = self.createSoup(os.path.join(
                        os.path.dirname(__file__),f'template/','HTML/','resources_template.html'))
                ol_tag = soup_new.find("ol")
                for resource in temp:
                    ol_tag.append(resource)

                self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','resources.html'), 
                    soup_new.prettify(formatter="html"))
            
            #login.html
            soup_new = self.createSoup(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','login.html'))
            new_title=soup_new.new_tag('title')
            new_title.string=f'{self.course_no} Interactive Offline Course'
            soup_new.html.head.title.replace_with(new_title)

            self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','login.html'), 
                    soup_new.prettify(formatter="html"))
            
            #progress.html
            if self.questions['final'] == None:
                soup_new = self.createSoup(os.path.join(os.path.dirname(__file__),'template/','HTML/','progress_template.html'))
                to_cmt = soup_new.find('div', class_='to_comment_out')
                to_cmt.replace_with(Comment(str(to_cmt)))

                self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','progress.html'), 
                    soup_new.prettify(formatter="html"))

            # print(soup_new)
            soup_new.find_all
            #JS FILES ---------------------------------------------------------------------------------------------------------------------
            set_score = ''
            set_module = '['
            for key, value in self.questions.items():
                if self.questions[key] == None:
                    if key != 'final':
                        set_score += f'\nmodule_quiz[{key}] = -2;'
                        set_module += f'{key},'
                    else:
                        set_score += f"\nmodule_quiz['{key}'] = -2;"
            set_module += ']'
            
            self.copy_file2(os.path.join(os.path.dirname(__file__),'template/','JS/','course.js'), 
                        os.path.join(os.path.dirname(__file__),f'{curr_dir}/','js/','course.js'),
                        'case "#X#":',"var modulesArray = '#X#'",
                        f'case {self.num_topics+1}:', f'var modulesArray = {set_module}')
            
            self.copy_file2(os.path.join(os.path.dirname(__file__),'template/','JS/','register.js'), 
                        os.path.join(os.path.dirname(__file__),f'{curr_dir}/','js/','register.js'),
                        'for (var i = 1; i <= "#X#" ; i++) {', "'#Write X#'", 
                        f"for (var i = 1; i <= {self.num_topics} ; i++) " +"{", set_score)
            
            self.copy_file(os.path.join(os.path.dirname(__file__),'template/','JS/','progress.js'), 
                        os.path.join(os.path.dirname(__file__),f'{curr_dir}/','js/','progress.js'),
                        "profile['current_module'] = '#X#';", 
                        f"profile['current_module'] = {self.num_topics};",)

            #CSS FILES ---------------------------------------------------------------------------------------------------------------------
            self.copy_file(os.path.join(os.path.dirname(__file__),'template/','CSS/','course.css'), 
                        os.path.join(os.path.dirname(__file__),f'{curr_dir}/','css/','course.css'),
                        '#module_content li:nth-of-type("#X#"){', f'#module_content li:nth-of-type({self.num_topics+2})'+"{")
            
            #quiz_htmls ---------------------------------------------------------------------------------------------------------------------
            for key,value in self.questions.items():
                # print(key,value)
                if self.questions[key] != None:
                    if key != 'final':
                        soup_new = self.createSoup(os.path.join(
                            os.path.dirname(__file__),'template/','HTML/','quiz_template.html'))
                        # new_title = soup_new.find('title')
                        new_title=soup_new.new_tag('title')
                        new_title.string=f'Topic {key} Quiz'
                        soup_new.html.head.title.replace_with(new_title)
                        new_h2 = soup_new.find("h2")
                        new_h2.string = f"Topic {key} Quiz"
                        # print(value)
                        self.write_script(soup_new, value)
                        
                        self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','quiz/',f'quiz{key}.html'), 
                            soup_new.prettify(formatter="html"))
                    else:
                        soup_new = self.createSoup(os.path.join(
                            os.path.dirname(__file__),'template/','HTML/','final-exam_template.html'))
                        self.write_script(soup_new, value)
                        self.write_to_html(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','quiz/','final-exam.html'), 
                            soup_new.prettify(formatter="html"))
            #modules
            for key, value in self.topics_dir.items():
                target = os.path.join(os.path.dirname(__file__),f'{curr_dir}/','modules')
                target_dir = os.path.join(target, f'Module{key}.pdf')
                shutil.copy2(self.topics_dir[key], target_dir)

            #banner
            file = ""
            match (self.faculty):
                case "Faculty of Education":
                    file = os.path.join(os.path.dirname(__file__),'template/','Banner/','Images/','FoE.png')
                case "Faculty of Information and Communication Studies":
                    file = os.path.join(os.path.dirname(__file__),'template/','Banner/','Images/','FICS.png')
                case "Faculty of Management and Development Studies":
                    file = os.path.join(os.path.dirname(__file__),'template/','Banner/','Images/','FMDS.png')
            with Image.open(file) as img:
                W, H = img.size
                font_name = ImageFont.truetype(os.path.join(
                    os.path.dirname(__file__),'template/','Banner/','Fonts/','lovtony.ttf'), 350)
                font_title = ImageFont.truetype(os.path.join(
                    os.path.dirname(__file__),'template/','Banner/','Fonts/','Sansus Webissimo-Regular.otf'), 100)
                draw = ImageDraw.Draw(img)
                _, _, w_name, h_name = draw.textbbox((0, 0), self.course_no, font=font_name)
                draw.text(((720+W-w_name)/2, ((H-h_name)/2)-100), self.course_no, font=font_name, fill='#8a1538')
                _, _, w_title, h_title = draw.textbbox((0, 0), self.course_title, font=font_title)
                draw.text(((720+W-w_title)/2, ((350+H-h_title)/2)), self.course_title, font=font_title, fill='#8a1538')
                img.save(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','img/','Logo.png'))
            
            #WRITE METADATA
            dictionary = {
                    "faculty": self.faculty,
                    "course_no": self.course_no,
                    "course_title": self.course_title,
                    "num_topics": self.num_topics,
                    "course_intro": self.course_intro,
                    "course_guide_dir": self.course_guide_dir,
                    "resources_dir": self.resources_dir,
                    "topics_dir": self.topics_dir,
                    "questions": self.questions
                }

            json_object = json.dumps(dictionary, indent=4)

            with open(os.path.join(os.path.dirname(__file__),f'{curr_dir}/','js/','metadata.json'), 'w') as file:
                file.write(json_object)
            #rename and copy file
            # os.rename(f'{curr_dir}',f'Interactive Offline Course/{self.course_no}')
            shutil.move(os.path.join(os.path.dirname(__file__),'Interactive Offline Course'), copy_dir)
            msg_box = CTkMessagebox(title='Success', message='Offline Course Package Created', icon='check', button_color=forest_green, button_hover_color=forest_green_d,)
        except Exception as error:
            print(error)
    def create_li_tag(self, to_append, soup, data_val, string):
        li_tag = soup.new_tag("li")
        a_tag = soup.new_tag("a", href="#")
        a_tag['data-value']=data_val
        a_tag.string = string
        li_tag.append(a_tag)
        to_append.append(li_tag)

    def write_script(self,soup_new, value):
        new_script = soup_new.find_all('script')[-1].getText()
        new_script = new_script.replace('ITEM_COUNT = "#X#"', f'ITEM_COUNT = {len(value)}')
        questions_json = json.dumps(value)
        encoded_questions = base64.b64encode(questions_json.encode()).decode()
        new_script = new_script.replace('var questions="#X#"','var encryptedQuestions="'
                                        +encoded_questions+'"\nvar questions = JSON.parse(atob(encryptedQuestions));')
        script_tag = soup_new.find_all("script")[-1]
        script_tag.string = new_script

    def copy_file(self,template, dir, to_replace, replace):
        shutil.copy2(template, dir)
        with open(dir,'r') as f:
            lines = f.read()
        lines = lines.replace(to_replace, replace)
        with open(dir,'w') as f:
            f.write(lines)

    def copy_file2(self,template, dir, to_replace1, to_replace2, replace1, replace2):
        shutil.copy2(template, dir)
        with open(dir,'r') as f:
            lines = f.read()
        lines = lines.replace(to_replace1, replace1)
        lines = lines.replace(to_replace2, replace2)
        with open(dir,'w') as f:
            f.write(lines)

    def tag_replace(self,soup_new,to_replace,replace):
        for tag in soup_new.find_all(string=re.compile(".*"+to_replace+".*")):
            if isinstance(tag, str):
                tag.replace_with(tag.replace(to_replace, replace))

    def write_to_html(self,html_file, html_output):
        try:
            directory = os.path.dirname(html_file)
            os.makedirs(directory,exist_ok=True)
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(html_output)
        except Exception as e:
            # print(f"{e}")
            pass

    def createSoup(self,dir):
        with open(dir, 'r') as html_report_part:
            soup = BeautifulSoup(html_report_part, 'html.parser')
            return copy.deepcopy(soup)
    
class CourseInfoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        course_info_page=ctk.CTkScrollableFrame(self,)
        course_info_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        course_info_page.grid_columnconfigure(0, weight=1)
        course_info_page.grid_columnconfigure(3, weight=1)

        footer = ctk.CTkFrame(self,height=80)
        footer.pack(side='bottom',fill='x',)
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=8)
        #FACULTY---------------------------------------------------------------------------------------------     
        faculty_label=ctk.CTkLabel(course_info_page, text='Faculty:',font=LARGEFONT)
        faculty_label.grid(row=1,column=1,sticky=ctk.W)        
        self.cb_var = ctk.StringVar()
        self.faculty_cb=ctk.CTkComboBox(course_info_page,state='readonly',
            values = [
                "Faculty of Education",
                "Faculty of Information and Communication Studies",
                "Faculty of Management and Development Studies",
                ],
            font=LARGEFONT,width=410,height=40,
            variable=self.cb_var, border_color='black')
        
        self.cb_var.trace_add(  # add a trace to watch cb_var
            'write',  # callback will be triggered whenever cb_var is written
            self.result  # callback function goes here!
        )
        self.faculty_cb.grid(row=2,column=1,sticky=ctk.W, columnspan=2)
        
        self.faculty_err=ctk.CTkLabel(course_info_page,text='',font=('Helvetica',9), text_color='red')
        self.faculty_err.grid(row=3,column=1,sticky=ctk.W,pady=0)
        #COURSE NO---------------------------------------------------------------------------------------------
        course_no_label=ctk.CTkLabel(course_info_page, text='Course No:',font=LARGEFONT)
        course_no_label.grid(row=4,column=1,sticky=ctk.W, columnspan=2)
        
        self.course_no_entry=ctk.CTkEntry(course_info_page,font=LARGEFONT,width=410,height=40, border_color='black')
        self.course_no_entry.grid(row=5,column=1,sticky=ctk.W, columnspan=2)

        self.course_no_err=ctk.CTkLabel(course_info_page,text='',font=('Helvetica',9), text_color='red')
        self.course_no_err.grid(row=6,column=1,sticky=ctk.W,pady=0)

        self.course_no_entry.bind('<Key>', lambda event:self.remove_err('course_no'))
        #COURSE TITLE---------------------------------------------------------------------------------------------
        course_title_label=ctk.CTkLabel(course_info_page, text='Course Title:',font=LARGEFONT)
        course_title_label.grid(row=7,column=1,sticky=ctk.W)
        
        self.course_title_entry=ctk.CTkEntry(course_info_page,font=LARGEFONT,width=410,height=40, border_color='black')
        self.course_title_entry.grid(row=8,column=1,sticky=ctk.W, columnspan=2)

        self.course_title_err=ctk.CTkLabel(course_info_page,text='',font=('Helvetica',9), text_color='red')
        self.course_title_err.grid(row=9,column=1,sticky=ctk.W,pady=0)

        self.course_title_entry.bind('<Key>', lambda event:self.remove_err('course_title'))
        #NUM TOPICS---------------------------------------------------------------------------------------------
        vcmd = (self.register(self.callback))

        num_topics_label=ctk.CTkLabel(course_info_page, text='Number of Topics:',font=LARGEFONT)
        num_topics_label.grid(row=10,column=1,sticky=ctk.W)
        
        self.num_topics_entry=ctk.CTkEntry(course_info_page,font=LARGEFONT,width=410,height=40, border_color='black',
                                           validate='all',validatecommand=(vcmd, '%P'))
        self.num_topics_entry.grid(row=11,column=1,sticky=ctk.W, columnspan=2)

        self.num_topics_err=ctk.CTkLabel(course_info_page,text='',font=('Helvetica',9), text_color='red')
        self.num_topics_err.grid(row=12,column=1,sticky=ctk.W,pady=0)
        #COURSE INTRO---------------------------------------------------------------------------------------------
        course_intro_label=ctk.CTkLabel(course_info_page, text='Course Introduction:',font=LARGEFONT)
        course_intro_label.grid(row=13,column=1,sticky=ctk.W)
        
        self.course_intro_tb=ctk.CTkTextbox(course_info_page, font=LARGEFONT, height=150, width=410)
        self.course_intro_tb.grid(row=14,column=1,sticky=ctk.W, columnspan=2)

        upload_btn = ctk.CTkButton(footer, text='Edit Existing Offline Course Package', font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                               command= lambda: self.edit_ocp())
        upload_btn.grid(row=1, column=0, sticky=ctk.E, padx=20, pady=20)
        
        save_btn=ctk.CTkButton(footer, text='Save', font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                               command= lambda: self.save())
        save_btn.grid(row=1, column=1, sticky=ctk.E, padx=20, pady=20)

    def save(self):
        valid = True

        if self.faculty_cb.get() == '':
            self.faculty_cb.configure(border_color='red')
            self.faculty_err.configure(text="Please select a faculty")
            valid = False
            
        if self.course_no_entry.get() == '':
            self.course_no_entry.configure(border_color='red')
            self.course_no_err.configure(text="Please enter the Course Number")
            valid = False

        if self.course_title_entry.get() == '':
            self.course_title_entry.configure(border_color='red')
            self.course_title_err.configure(text="Please enter the Course Title")
            valid = False

        if self.num_topics_entry.get() == '' or int(self.num_topics_entry.get()) < 1 :
            self.num_topics_entry.configure(border_color='red')
            self.num_topics_err.configure(text="Please enter a valid Number of Topics (>0)")
            valid = False

        if valid:
            temp=self.course_intro_tb.get("1.0", 'end-1c').strip()
            course_intro = [temp1.strip() for temp1 in temp.split('\n') if temp1.strip()]
            # print(course_intro)
            self.controller.save_course_info(
                self.faculty_cb.get(),
                self.course_no_entry.get().upper(),
                self.course_title_entry.get(),
                int(self.num_topics_entry.get()),
                course_intro
                )
            msg_box =CTkMessagebox(title='Success', message='Course Info Saved', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)

    def result(self, *args):  # add *args to accomodate the vals passed by the trace
        self.remove_err('faculty')

    def callback(self, P):
        self.remove_err('num_topics')
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def remove_err(self, err_label):
        if err_label == 'faculty':
            self.faculty_cb.configure(border_color='black')
            self.faculty_err.configure(text='')
        if err_label == 'course_no':
            self.course_no_entry.configure(border_color='black')
            self.course_no_err.configure(text='')
        if err_label == 'course_title':
            self.course_title_entry.configure(border_color='black')
            self.course_title_err.configure(text='')
        if err_label == 'num_topics':
            self.num_topics_entry.configure(border_color='black')
            self.num_topics_err.configure(text='')

    def edit_ocp(self):
        json_file='metadata.json'

        source = '{}'.format(filedialog.askdirectory(title='Select Folder'))
        if source:
            for root, dir, files in os.walk(source):
                if json_file in files:
                    # print('metadata found')

                    json_path = os.path.join(root, json_file)
                    with open(json_path, 'r') as json_file:
                        data = json.load(json_file)

                        self.controller.save_course_info(
                            data['faculty'],
                            data['course_no'],
                            data['course_title'],
                            data['num_topics'],
                            data['course_intro']
                        )

                        self.controller.save_course_guide(data['course_guide_dir'])
                        self.controller.save_resources_dir(data['resources_dir'], 'Exist')
                        self.controller.save_topics_dir(data['topics_dir'])
                        self.controller.save_questions(data['questions'])

                        self.course_no_entry.delete(0, last_index=ctk.END)
                        self.course_title_entry.delete(0, last_index=ctk.END)
                        self.num_topics_entry.delete(0, last_index=ctk.END)
                        self.course_intro_tb.delete('1.0', index2=ctk.END)

                        self.faculty_cb.set(data['faculty'])
                        self.course_no_entry.insert(ctk.END, data['course_no'])
                        self.course_title_entry.insert(ctk.END, data['course_title'])
                        self.num_topics_entry.insert(ctk.END, data['num_topics'])
                        for x in data['course_intro']:
                            self.course_intro_tb.insert(ctk.END, x+'\n')
            msg_box =CTkMessagebox(title='Success', message='Metadata Found', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)

class ResourcesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        self.resources_page=ctk.CTkFrame(self)
        self.resources_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        self.resources_page.grid_columnconfigure(0, weight=1)
        self.resources_page.grid_columnconfigure(2, weight=1)

    def update(self):
        course_guide_dir = self.controller.get_course_guide_dir()
        if course_guide_dir != '':
            btn_text = 'Change Course Guide'
        else:
            btn_text = 'Upload Course Guide'

        self.course_guide_btn = ctk.CTkButton(self.resources_page,text=btn_text, font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                        command=lambda value='Course Guide': self.save_dirs(value))
        self.course_guide_btn.grid(row=1,column=1,sticky=ctk.W,pady=20)

        resources_btn = ctk.CTkButton(self.resources_page,text='Add Folders', font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                        command=lambda value='Folder': self.save_dirs(value))
        resources_btn.grid(row=2,column=1,sticky=ctk.W,pady=20)

        files_btn = ctk.CTkButton(self.resources_page,text='Add Files', font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                        command=lambda value='File': self.save_dirs(value))
        files_btn.grid(row=3,column=1,sticky=ctk.W,pady=20)

        resources_dir = self.controller.get_resources_dir()    
        print(resources_dir)    
        
        resources_dir_label=ctk.CTkLabel(self.resources_page, text='Resources Directory:',font=LARGEFONT)
        resources_dir_tb=ctk.CTkTextbox(self.resources_page, font=LARGEFONT, height=150, width=410)
        for x in resources_dir:
            resources_dir_tb.insert(ctk.END,x[0]+'\n')
        resources_dir_tb.configure(state=ctk.DISABLED)
        
        resources_dir_label.grid(row=4,column=1,sticky=ctk.W, columnspan=2)
        resources_dir_tb.grid(row=5,column=1,sticky=ctk.W, columnspan=2)
     

        files_btn = ctk.CTkButton(self.resources_page,text='Remove Resources', font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                        command=lambda: self.check_resources())
        files_btn.grid(row=6,column=1,sticky=ctk.W,pady=20)

    def save_dirs(self, button_name):
        if button_name == 'Course Guide':
            source = filedialog.askopenfilename(initialdir='/', title='Select Course Guide',
                                            filetypes=(('PDF', '*.pdf'), ("All Files", '*.*'),))
        elif button_name == 'Folder':
            source = '{}'.format(filedialog.askdirectory(title='Select Folder'))
        elif button_name == 'File':
            source = filedialog.askopenfilename(initialdir='/', title='Select file',
                                            filetypes=(('All Files', ''),))
        
        if source:
            if button_name == 'Course Guide':
                self.controller.save_course_guide(source)
                self.course_guide_btn.configure(text='Change Course Guide')
                msg_box =CTkMessagebox(title='Success', message='Course Guide Uploaded', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
                self.update()
            else:
                self.controller.save_resources_dir(source, button_name)
                msg_box =CTkMessagebox(title='Success', message='Resources Uploaded', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
                self.update()

    def check_resources(self):
        resources_dir = self.controller.get_resources_dir()
        if len(resources_dir) == 0:
            msg_box = CTkMessagebox(title='Error', message='No Resources Available.',icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)
        else:
            self.controller.refresh_delResourcePage()
            self.controller.indicate(self.controller.resources_btn,DelResourcesPage)

class DelResourcesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        del_resources_page=ctk.CTkFrame(self,)
        del_resources_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        del_resources_page.grid_columnconfigure(0, weight=1)
        del_resources_page.grid_columnconfigure(2, weight=1)

        footer = ctk.CTkFrame(self,height=80)
        footer.pack(side='bottom',fill='x',)
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=8)

        self.lb2 = CTkListbox(del_resources_page,height=10, width=410,font=LARGEFONT, fg_color=('white', 'black'), text_color=('black', 'white'))
        self.lb2.grid(row=2,column=1,sticky=ctk.W, columnspan=2,pady=20)

        delete_btn=ctk.CTkButton(footer,text="Delete",font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                                    command=lambda: self.del_resources())
        delete_btn.grid(row=1,column=1,sticky=ctk.E,padx=20, pady=20)

        back_btn=ctk.CTkButton(footer,text="Back",font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                                    command=lambda: [
                                    self.controller.refresh_resourcesPage(),
                                    self.controller.indicate(self.controller.resources_btn,ResourcesPage)
                                    ])
        back_btn.grid(row=1,column=0,sticky=ctk.E,padx=20, pady=20)

    def update_lb(self):
        resources_dir = self.controller.get_resources_dir()
        if len(resources_dir) != 0 and self.lb2.size() != 0:
            self.lb2.delete('all')
        for x in range(len(resources_dir)):
            self.lb2.insert(x, resources_dir[x][0])

    def del_resources(self):
        try:
            selection = self.lb2.curselection()
            self.lb2.delete(selection)
            self.controller.delete_resource_dir(selection)
            self.controller.refresh_resourcesPage()
            self.controller.indicate(self.controller.resources_btn, ResourcesPage)
            # msg_box =CTkMessagebox(title='Success', message='Resource Deleted', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
            # if self.lb2.size()==0:
            #     self.controller.refresh_resourcesPage()
            #     self.controller.indicate(self.controller.resources_btn, ResourcesPage)
        except:
            msg_box = CTkMessagebox(title='Error', message='Please select a file/folder to delete.',icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)

class UploadTopicsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        self.upload_topics_page=ctk.CTkScrollableFrame(self,)
        self.upload_topics_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        self.upload_topics_page.grid_columnconfigure(0, weight=1)
        self.upload_topics_page.grid_columnconfigure(2, weight=1)

    def update_btns(self):
        topics_dir = self.controller.get_topics_dir()
        # print(num_topics, topics_dir)
        for x in self.upload_topics_page.winfo_children():
            x.destroy()

        for k in topics_dir.keys():
            btn_text = ''
            if topics_dir[k] != None:
                btn_text = f'Change Topic {k} PDF'
            else:
                btn_text = f'Upload Topic {k} PDF'
            btn = ctk.CTkButton(self.upload_topics_page,text=btn_text, font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                        command=lambda value=k: self.save_topics_dir(value))
            btn.grid(row=k,column=1,sticky=ctk.W,pady=20)

    def save_topics_dir(self, value):
        source = filedialog.askopenfilename(initialdir='/', title=f'Select Topic {value} PDF',
                                            filetypes=(('PDF', '*.pdf'), ("All Files", '*.*'),))
        topics_dir = self.controller.get_topics_dir()
        if source:
            topics_dir[value] = source
            self.controller.save_topics_dir(topics_dir)
            msg_box =CTkMessagebox(title='Success', message=f'Topic {value} PDF Uploaded', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
            self.update_btns()

class CreateQuizPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        
        self.controller = controller

        self.create_quiz_page=ctk.CTkScrollableFrame(self,)
        self.create_quiz_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        self.create_quiz_page.grid_columnconfigure(0, weight=1)
        self.create_quiz_page.grid_columnconfigure(3, weight=1)

        footer = ctk.CTkFrame(self,height=80)
        footer.pack(side='bottom',fill='x',)
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=8)

        upload_btn = ctk.CTkButton(footer, text='Download GIFT Format', font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                               command= lambda: self.downloadGift())
        upload_btn.grid(row=1, column=0, sticky=ctk.E, padx=20, pady=20)
        
        webopen_btn=ctk.CTkButton(footer, text='What is GIFT format?', font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                               command= lambda: [
                                subprocess.Popen(["open", os.path.join(os.path.dirname(__file__),'manuals/','GIFTManual.pdf')])
                                # webbrowser.open_new(os.path.join(os.path.dirname(__file__),'manuals/','GIFTManual.pdf'))
                                ])
        webopen_btn.grid(row=1, column=1, sticky=ctk.E, padx=20, pady=20)

    def downloadGift(self):
        path = '{}'.format(filedialog.askdirectory(title='Select Folder'))
        if path:
            shutil.copy2(os.path.join(os.path.dirname(__file__), 'manuals/', 'GIFT Template.txt'), os.path.join(path, 'GIFT Template.txt'))

    def update_btns(self):
        questions = self.controller.get_questions()
        for x in self.create_quiz_page.winfo_children():
            x.destroy()

        for k in questions.keys():
            btn_text = ''
            if questions[k] != None:
                if k != 'final':
                    btn_text = f'Change Quiz {k}'
                    del_btn = ctk.CTkButton(self.create_quiz_page,text='Delete', font=LARGEFONT,width=10,height=40,fg_color=up_maroon,hover_color=up_maroon_d,
                                command=lambda value=k: self.delete(value))
                    del_btn.grid(row=k,column=1,sticky=ctk.E,pady=20)
                    btn = ctk.CTkButton(self.create_quiz_page,text=btn_text, font=LARGEFONT,width=355,height=40,fg_color=forest_green, hover_color=forest_green_d,
                                command=lambda value=k: [self.create_quiz(value)])
                    btn.grid(row=k,column=2,sticky=ctk.W,pady=20)
                elif k == 'final':
                    btn_text = f'Change Final Quiz'
                    del_btn = ctk.CTkButton(self.create_quiz_page,text='Delete', font=LARGEFONT,width=10,height=40,fg_color=up_maroon, hover_color=up_maroon_d,
                                command=lambda value=k: self.delete(value))
                    del_btn.grid(row=len(questions),column=1,sticky=ctk.E,pady=20)
                    btn = ctk.CTkButton(self.create_quiz_page,text=btn_text, font=LARGEFONT,width=355,height=40,fg_color=forest_green, hover_color=forest_green_d,
                                command=lambda value=k: [self.create_quiz(value)])
                    btn.grid(row=len(questions),column=2,sticky=ctk.W,pady=20)
            elif questions[k] == None and k == 'final':
                btn_text = f'Create Final Quiz'
                btn = ctk.CTkButton(self.create_quiz_page,text=btn_text, font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                                command=lambda value=k: [self.create_quiz(value)])
                btn.grid(row=len(questions),column=1,sticky=ctk.W,pady=20, columnspan=2)
            else:
                btn_text = f'Create Quiz {k}'
                btn = ctk.CTkButton(self.create_quiz_page,text=btn_text, font=LARGEFONT,width=410,height=40,fg_color=forest_green, hover_color=forest_green_d,
                                command=lambda value=k: [self.create_quiz(value)])
                btn.grid(row=k,column=1,sticky=ctk.W,pady=20, columnspan=2)
         
    def delete(self,value):
        questions = self.controller.get_questions()
        questions[value] = None
        self.controller.save_questions(questions)
        msg_box =CTkMessagebox(title='Success', message='Quiz Deleted', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
        self.update_btns()

    def create_quiz(self, value):
        questions = self.controller.get_questions()
        source = filedialog.askopenfilename(initialdir='/', title=f'Select txt file',
                                            filetypes=(('Text', '*.txt'), ("All Files", '*.*'),))
        
        temp_questions = []
        if source:
            with open (source, 'r') as file:
                lines = file.readlines()

            result_arrays = []
            current_array = []

            for line in lines:
                if line== '\n':
                    result_arrays.append(current_array)
                    current_array = []
                else:
                    current_array.append(line.strip())

            if current_array:
                result_arrays.append(current_array)

            for x in result_arrays:
                current_question = {
                        'label': None,
                        'options':[],
                        'answer':[]
                    }
                is_valid_question = True
                shuffleFlag = False
                for y in x:
                    if y.startswith("{~%") or y.startswith('~%'):
                        is_correct = False
                        if y.startswith('{~%100%') or y.startswith('~%100%'):
                            is_correct = True
                        line_parts = y.split('%')
                        if len(line_parts) == 3:
                            temp = line_parts[2]
                            if temp.endswith('}'):
                                temp = temp[:-1]
                            elif temp.endswith('}S'):
                                temp = temp[:-2]
                                shuffleFlag = True                            
                            current_question['options'].append(temp)
                            if is_correct:
                                current_question['answer'].append(temp)
                        else:
                            is_valid_question = False
                    else:
                        current_question['label'] = y
                
                if shuffleFlag:
                    random.shuffle(current_question['options'])

                if is_valid_question:
                    temp_questions.append(current_question)
                else:
                    # print('Invalid question format detected.')
                    # pass
                    msg_box = CTkMessagebox(title='Error', message=f'Invalid question format detected on line {x}',icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)

            if temp_questions != []:
                questions[value] = temp_questions
                self.controller.save_questions(questions)
                msg_box =CTkMessagebox(title='Success', message='Quiz Uploaded', icon='check',button_color=forest_green, button_hover_color=forest_green_d,)
                self.update_btns()
        else: 
            questions[value] = None
            self.controller.save_questions(questions)
            msg_box = CTkMessagebox(title='Error', message='Not a valid file format', icon="cancel",button_color=forest_green, button_hover_color=forest_green_d,)

class CreateOCPPage(ctk.CTkFrame):    
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        self.create_ocp_page=ctk.CTkScrollableFrame(self,)
        self.create_ocp_page.pack(anchor= ctk.CENTER, fill='both', expand=True)
        self.create_ocp_page.grid_columnconfigure(0, weight=1)
        self.create_ocp_page.grid_columnconfigure(2, weight=1)

        footer = ctk.CTkFrame(self,height=80)
        footer.pack(side='bottom',fill='x',)
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=8)

        save_btn=ctk.CTkButton(footer, text='Create OCP', font=LARGEFONT,height=50,width=215,fg_color=forest_green, hover_color=forest_green_d,
                               command= lambda: self.create_ocp())
        save_btn.grid(row=1, column=1, sticky=ctk.E, padx=20, pady=20)

    def update_details(self):
        faculty = self.controller.get_faculty()
        course_no = self.controller.get_course_no()
        course_title = self.controller.get_course_title()
        course_intro = self.controller.get_course_intro()
        course_guide_dir = self.controller.get_course_guide_dir()
        resources_dir = self.controller.get_resources_dir()
        topics_dir = self.controller.get_topics_dir()
        questions = self.controller.get_questions()

        for x in self.create_ocp_page.winfo_children():
            x.destroy()

        faculty_label=ctk.CTkLabel(self.create_ocp_page, text='Faculty:',font=LARGEFONT)
        faculty_entry=ctk.CTkEntry(self.create_ocp_page,font=LARGEFONT,width=410,height=40,)
        faculty_entry.insert(ctk.END, faculty)
        faculty_entry.configure(state=ctk.DISABLED)

        faculty_label.grid(row=1,column=1,sticky=ctk.W, columnspan=2)
        faculty_entry.grid(row=2,column=1,sticky=ctk.W, columnspan=2)

        course_no_label=ctk.CTkLabel(self.create_ocp_page, text='Course No:',font=LARGEFONT)
        course_no_entry=ctk.CTkEntry(self.create_ocp_page,font=LARGEFONT,width=410,height=40,)
        course_no_entry.insert(ctk.END, course_no)
        course_no_entry.configure(state=ctk.DISABLED)

        course_no_label.grid(row=3,column=1,sticky=ctk.W, columnspan=2)
        course_no_entry.grid(row=4,column=1,sticky=ctk.W, columnspan=2)
        
        course_title_label=ctk.CTkLabel(self.create_ocp_page, text='Course Title:',font=LARGEFONT)
        course_title_entry=ctk.CTkEntry(self.create_ocp_page,font=LARGEFONT,width=410,height=40,)
        course_title_entry.insert(ctk.END, course_title)
        course_title_entry.configure(state=ctk.DISABLED)

        course_title_label.grid(row=5,column=1,sticky=ctk.W, columnspan=2)
        course_title_entry.grid(row=6,column=1,sticky=ctk.W, columnspan=2)

        
        if course_intro != []:
            course_intro_label=ctk.CTkLabel(self.create_ocp_page, text='Course Introduction:',font=LARGEFONT)
            course_intro_tb=ctk.CTkTextbox(self.create_ocp_page, font=LARGEFONT, height=150, width=410)
            for x in course_intro:
                course_intro_tb.insert(ctk.END,x+'\n')
            course_intro_tb.configure(state=ctk.DISABLED)
            
            course_intro_label.grid(row=7,column=1,sticky=ctk.W, columnspan=2)
            course_intro_tb.grid(row=8,column=1,sticky=ctk.W, columnspan=2)

        course_guide_dir_label=ctk.CTkLabel(self.create_ocp_page, text='Course Guide Directory:',font=LARGEFONT)
        course_guide_dir_entry=ctk.CTkEntry(self.create_ocp_page,font=LARGEFONT,width=410,height=40,)
        course_guide_dir_entry.insert(ctk.END, course_guide_dir)
        course_guide_dir_entry.configure(state=ctk.DISABLED)

        course_guide_dir_label.grid(row=9,column=1,sticky=ctk.W, columnspan=2)
        course_guide_dir_entry.grid(row=10,column=1,sticky=ctk.W, columnspan=2)

        if resources_dir != []:
            resources_dir_label=ctk.CTkLabel(self.create_ocp_page, text='Resources Directory:',font=LARGEFONT)
            resources_dir_tb=ctk.CTkTextbox(self.create_ocp_page, font=LARGEFONT, height=150, width=410)
            for x in resources_dir:
                resources_dir_tb.insert(ctk.END,x[0]+'\n')
            resources_dir_tb.configure(state=ctk.DISABLED)
            
            resources_dir_label.grid(row=11,column=1,sticky=ctk.W, columnspan=2)
            resources_dir_tb.grid(row=12,column=1,sticky=ctk.W, columnspan=2)

        topics_dir_label=ctk.CTkLabel(self.create_ocp_page, text='Topics Directory:',font=LARGEFONT)
        topics_dir_tb=ctk.CTkTextbox(self.create_ocp_page, font=LARGEFONT, height=150, width=410)
        for key, value in topics_dir.items():
            topics_dir_tb.insert(ctk.END,f'Topic {key}: {value}\n\n')
        topics_dir_tb.configure(state=ctk.DISABLED)

        topics_dir_label.grid(row=13,column=1,sticky=ctk.W, columnspan=2)
        topics_dir_tb.grid(row=14,column=1,sticky=ctk.W, columnspan=2)

        row = 15
        for key, value in questions.items():
            if value != None:
                if key != 'final':
                    questions_label=ctk.CTkLabel(self.create_ocp_page, text=f'Quiz {key}',font=LARGEFONT)
                else:
                    questions_label=ctk.CTkLabel(self.create_ocp_page, text=f'Final Exam',font=LARGEFONT)

                questions_tb=ctk.CTkTextbox(self.create_ocp_page, font=LARGEFONT, height=150, width=410)
                
                for x in value:
                    questions_tb.insert(ctk.END, x['label']+'\n')
                    for y in x['options']:
                        if y in x['answer']:
                            questions_tb.tag_config('correct', background=forest_green, foreground='white')
                            questions_tb.insert(ctk.END, y+'\n', 'correct')
                        else:
                            questions_tb.insert(ctk.END, y+'\n')
                    questions_tb.insert(ctk.END,'\n')
                questions_tb.configure(state=ctk.DISABLED)

                questions_label.grid(row=row,column=1,sticky=ctk.W, columnspan=2)
                questions_tb.grid(row=row+1,column=1,sticky=ctk.W, columnspan=2)

                row = row+2

    def create_ocp(self):
        self.controller.create_ocp()

if __name__ == '__main__':
    app = OCPWizApp()
    app.mainloop()
