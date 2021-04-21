import subprocess,os
from tabulate import tabulate
import re
from termcolor import colored

class Simplified:
    def __init__(self):
        self.option_fn = dict()
        self.def_port = ''
    
    # First step in a build-process is writing the docker file. 
    def create_dockerfile(self, lang,image,path,req_dependencies, setup_command, cmd):
        ######### Writing docker file ############
        f = open(path + "/Dockerfile", "w")

        #Specifying base IMAGE name according to the LANGUAGE used.
        f.write('FROM ' + image + '\n')

        #Specifying required dependencies of the application (Example: g++ for node.js, make for node.js)
        if req_dependencies != '':
            f.write('RUN '+ req_dependencies + '\n')

        #Specifying WORK directory so that docker uses this PATH as default location for subsequent COMMANDS.
        f.write('WORKDIR /' + path + '\n')

        #Instructs docker to copy ALL contents of application folder to WORK directory.
        f.write('COPY . .\n')

        #Specify command to import specific dependencies of project (Example: YARN for node.js, PIP for python3 projects.)
        f.write('RUN ' + setup_command + '\n')
        #f.write('RUN yarn install --production\n')

        #Specify the LAUNCH command that needs to run LAST. (Example: node example.js or python3 -m flask run)
        final_cmd = 'CMD ['
        for c in cmd:
            final_cmd = final_cmd + '"' + c + '", '
        final_cmd = final_cmd[:len(final_cmd)-2] + ']'
        f.write(final_cmd)

        f.close()

    # BUILD IMAGE: Take required inputs from USER to carry out docker build 
    def build_new(self):
        #Currently supported frameworks: Node.js web app and python web-app using FLASK
        langs = ["Node.js","Python-flask"]
        table = []
        for i,lang in enumerate(langs):
            row = [str(i), lang]
            table.append(row)
        
        #tabulate: Beautifying user-driven options menu
        print(tabulate(table,headers=["Code","Language"]))

        #Take input for the LANGUAGE used in the project
        ip = input('Please provide the code for the language used for your project: ')

        #Take input for the SOURCE-PATH of the project-folder
        path = input("Please provide folder name of the application: ")
        
        if ip == '0':
            #Docker images can be inherited from base-images (just like INHERITANCE in OOP)
            #specifying base image so that we do not need to implement all functionalities needed in a NODE app.
            image = 'node:12-alpine'

            #node apps need python, g++ and make tool to be pre-installed.
            req_dependencies = 'apk add --no-cache python g++ make'
            
            #Use YARN or NPM to install all dependencies in package.json
            setup_command = 'yarn install --production'

            #Node.js needs the source JS file to launch application
            src = input("Please enter the path of your launch file: ")
            cmd = 'node ' + src
        elif ip == '1':
            image = 'python:3.8-slim-buster'
            req_dependencies = ''
            setup_command = 'pip3 install flask'
            cmd = 'python3 -m flask run --host=0.0.0.0 --port=3000'
        else:
            print(colored('Invalid input. ','red'))
            return
        
        cnf = input('Please confirm the launch command: ' + colored(cmd,'green') + '\n' +'Press 1 to confirm, 0 to enter manually: ')
        if cnf == '0':
            cmd = input("Enter command: ")
            cmd = cmd.split()
        elif cnf == '1':
            cmd = cmd.split()
        else:
            print('Invalid')
            return
        self.create_dockerfile(lang,image,path,req_dependencies, setup_command, cmd)
        return self.build(True, path)

    def build(self, new = False, path = None):
        if new:
            pref_image_name = input("Please enter your preferred image name(-1 to go back): ")
            if pref_image_name == '-1':
                self.clear()
                return
        else:
            image_names = self.display_images()
            img_num = input("Please input the image number to build(-1 to go back): ")
            if img_num == '-1':
                self.clear()
                return
            pref_image_name = image_names[int(img_num)]
            path = input('Enter folder name of app: ')

        build_success = subprocess.run(["docker","build","-t",pref_image_name,"."],cwd=path + '/')

        
        if build_success.returncode == 0:
            print(colored("\n##########  Build Success #########",'green'))
            return pref_image_name
        else:
            print(colored("\n##########  Build Failed #########",'red'))
        return '-1'
    
    def run(self, img=None):
        port = "3000"
        if img == None:
            image_names = self.display_images()
            img_num = input("Please input the image number to run(-1 to go back): ")
            if img_num == '-1':
                self.clear()
                return
            pref_image_name = image_names[int(img_num)]
        else:
            pref_image_name = img
        ip = '1'
        while(ip == '1'):
            run_success = subprocess.run(["docker", "run", "-dp", port+':3000', pref_image_name],text=True,stderr=subprocess.PIPE)
            print(run_success.stderr)
            if run_success.returncode==0:
                print(colored("##########  Run Success #########",'green'),"PORT: "+port)
                return port
            elif "port is already allocated" in run_success.stderr:
                port = input(colored("Port is already allocated",'red') + 'please enter a new port(-1 to go back): ')
                if ip == '-1':
                    return '-1'
            else:
                print(colored("##########  Run Failed #########",'red'),"PORT: "+port)
                return '-1'
        return '-1'  
        

    def launch(self, port = None):
        if port == None:
            image_names = self.display_running_containers()
            selection = int(input("Please input the code to launch(-1 to go back): "))
            if selection == -1:
                self.clear()
                return
            port = image_names[selection][2]
            port = port.split(':')[1].split('-')[0]
        launch_success = subprocess.run(["open", "-a", "Google Chrome", "http://localhost:"+port],text=True)
        if launch_success.returncode==0:
            print (colored("\n##########  Launch Success #########","green"))
        else:
            print(colored("\n##########  Launch Failed #########",'red'))
        

    def display_running_containers(self):
        images = subprocess.run(["docker","ps"],stdout=subprocess.PIPE, text = True)
        images = images.stdout.splitlines()
        image_names = []
        port = ''
        for lines in images[1:]:
            for word in lines.split():
                if word.endswith('tcp'):
                    port = word
            row = [lines.split()[0],lines.split()[1],port]
            image_names.append(row)
        table = []
        ########## LIST ALL RUNNING CONTAINERS #############
        for i,img in enumerate(image_names):
            row = [str(i), img[0], img[1], img[2]]
            table.append(row)

        print(tabulate(table,headers=["Code","Container ID", "Image Names", "Port"]))
        print('\n\n\n')
        return image_names 
    def display_images(self):
        images = subprocess.run(["docker","image", "ls"],stdout=subprocess.PIPE, text = True)
        images = images.stdout.splitlines()
        image_names = []
        for lines in images[1:]:
            image_names.append(lines.split()[0])
        table = []
        ########## LIST ALL IMAGES #############
        for i,img in enumerate(image_names):
            row = [str(i), img]
            table.append(row)
            #print(i, img, sep = ':  ')
        print(tabulate(table,headers=["Code","Image Names"]))
        print('\n\n\n')
        return image_names

    def scan(self):
        image_names = self.display_images()
        img_num = input("Please input the image number to scan(-1 to go back): ")
        if img_num == '-1':
            self.clear()
            return
        img_to_scan = image_names[int(img_num)]
        subprocess.run(["docker","scan",img_to_scan])


    def exit(self):
        ip = input('Are you sure you want to exit?(Y/N): ')
        if ip=='Y':
            exit()
    
    def display_options(self):
        options = [colored("Exit",'red'),colored("Build new app",'green'),colored("Re-build app","green"),colored("Run existing app","green"), colored("Stop and remove app",'red'),colored("Launch app","green"), colored("Scan vulnerabilities",'red'), colored("Display running containers","green"), colored("Display available images","green"), "Clear console", colored("Build-Run and Launch","green")]
        self.option_fn = {'0':self.exit,'1':self.build_new,'2':self.build,'3':self.run,'4':self.stop_container,'5':self.launch,'6':self.scan, '7':self.display_running_containers, '8':self.display_images, '9':self.clear, '10':self.build_run_launch}
        table = []
        for i,option in enumerate(options):
            #print(i, option, sep="|\t")
            row = [str(i),option]
            table.append(row)
        print(tabulate(table,headers=["Code", "Options"]))
    
    def stop_container(self):
        image_names = self.display_running_containers()
        selection = int(input("Enter container number to stop(-1 to go back): "))
        if selection == -1:
            self.clear()
            return
        stop_success = subprocess.run(["docker","rm","-f",image_names[selection][0]])
        if stop_success.returncode == 0:
            print(colored("#############    Stop Success ##############", 'red'))
        else:
            print(colored("\n##########  Stop Failed #########",'red'))

    def clear(self):
        subprocess.run(["clear"])
        self.welcome()

    def welcome(self):
        print(colored("##################################################################################","blue"))
        print('\t\t',colored("Welcome to"),colored("Docker Simplified","green"))
        print(colored("##################################################################################","blue"))

    def build_run_launch(self):
        img = self.build_new()
        if img == '-1':
            print(colored("Build Failed","red"))
            return
        port = self.run(img)
        if port == -1:
            print(colored("Run Failed","red"))
            return
        x = input("Want to launch(Y/N): ")
        if x == 'Y':
            self.launch(port)


user = Simplified()
user.welcome()

selection = 1

while True:
    user.display_options()
    selection = input("Enter code: ")
    fn = user.option_fn.get(selection,0)
    if fn == 0:
        print("Invalid input\nRetry\n")
    else:
        fn()






        