import subprocess

images = subprocess.run(["docker","image", "ls"],stdout=subprocess.PIPE, text = True)

images = images.stdout.splitlines()
image_names = []
for lines in images[1:]:
    image_names.append(lines.split()[0])


########## LIST ALL IMAGES #############
for i,img in enumerate(image_names):
    print(i, img, sep = ':  ')
print('\n\n\n')


img_num = input("Please input the image number to scan: ")
img_to_scan = image_names[int(img_num)]

subprocess.run(["docker","scan",img_to_scan])


