# make a docker file

#take image as input from user

#prompt user for input
lang = input('Please provide the language used for your project: ')

if lang == 'Node.js':
    image = 'node:12-alpine'
    langShort = 'node'

#prompt user for src file input
src = input('Please provide the source file path of project: ')

f = open("app/Dockerfile", "w")

######### Writing docker file ############

#Specifying image name
f.write('FROM ' + image + '\n')

#Specifying required dependencies
f.write('RUN apk add --no-cache python g++ make\n')

#Specifying working directory
f.write('WORKDIR /app\n')

#Copy to current directory
f.write('COPY . .\n')

#RUN setup
f.write('RUN yarn install --production\n')

#Specify source file
f.write('CMD [' + '"' + langShort + '", "' + src + '"]\n' )

f.close()

import subprocess,os
pref_image_name = input("Please enter your preferred image name: ")

build_success = subprocess.run(["docker","build","-t",pref_image_name,"."],cwd='app/')

##########  build success #########
if build_success.returncode == 0:
    #prompt for run ?
    ip = input("Please enter 1 for scanning image or 2 for running container with " + pref_image_name + " image? (1/2)")
    if ip == '2':
        run_success = subprocess.run(["docker", "run", "-dp", "3000:3000", pref_image_name])
        if run_success.returncode==0:
            print("Started successfully!!!")
            launch = input("Do you want to launch the application? (Y/N)")
            launch_success = subprocess.run(["open", "-a", "Google Chrome", "http://localhost:3000"])
            if launch_success.returncode==0:
                print ("Launch success")
    elif ip == '1':
        scan_success = subprocess.run(["docker","scan",'-f','app/Dockerfile',pref_image_name])
        if scan_success.returncode==0:
            print("Scan complete.")
            



