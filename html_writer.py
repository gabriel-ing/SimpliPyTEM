from airium import Airium
import os

def write_html(images, videos, title='Default_experiment_title', **kwargs):
    a =Airium()
    with a.html(lang='en'):
        with a.head():
            a.meta(charset='utf-8', content='width=device-width')
            a.title(_t='')
            a.link(href="style.css", rel='stylesheet', type='text/css')
        with a.body():
            with a.div(klass='banner'):
                with a.h1():
                    a(title.replace('_', ' '))
            with a.h2():
                a('Images')
            for image in images:
                with a.div(klass='Image_group'):

                    with a.h3():
                        a(image.strip('.jpg').split('/')[-1].replace('_', ' '))
                    a.img(src=image, alt='Alt text')    
            with a.h2():
                a('Videos')
            for video in videos:
                with a.div(klass='Video_group'):
                    with a.h3():
                        a(video.strip('.mp4').split('/')[-1].replace('_',' '))
                    with a.video('controls', width=500,height=460):
                        a.source(src=video, type="video/mp4")


        if 'outdir' in kwargs:
            outdir = kwargs['outdir']
            title = outdir + '/' + title
        if title[-5:]!='.html':
            title = title+'.html'


    with open(title, 'w') as f:
        f.write(str(a))        



def get_files(directory, imagedir, videodir, image_pattern='', video_pattern=''):
    current_dir = os.getcwd()
    os.chdir(directory) 
    image_files = [imagedir+'/'+x for x in os.listdir(imagedir) if x[-3:]=='jpg' and image_pattern in x]
    #print(image_files)
    video_files = [videodir+'/'+x for x in os.listdir(videodir) if x[-3:]=='mp4' and video_pattern in x]
    #print(video_files)
    os.chdir(current_dir)
    return image_files, video_files

if __name__=='__main__':
    images, videos = get_files('.', 'Images', 'Videos')
    write_html(images,videos)    

