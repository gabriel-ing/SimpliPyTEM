import os
import re
import ncempy.io as nci

from SimpliPyTEM.Micrograph_class import default_image_pipeline
from SimpliPyTEM.MicroVideo_class import default_video_pipeline

def video_processing(
    filename,
    output_folder_name,
    output_type,
    contrast_enhance,
    xybin,
    medfilter,
    gaussian_filter,
    scalebar_on,
    video_status,
    topaz_denoise,
    denoise_with_cuda,
):
    print('Contrast enhance {}'.format(contrast_enhance))
    if video_status == "Save Average":
        default_image_pipeline(
            filename,
            output_type=output_type,
            contrast_enhance=contrast_enhance,
            xybin=xybin,
            medfilter=medfilter,
            gaussfilter=gaussian_filter,
            scalebar=scalebar_on,
            outdir=output_folder_name,
            topaz_denoise=topaz_denoise,
            denoise_with_cuda=denoise_with_cuda,
        )
    else:
        default_video_pipeline(
            filename,
            vid_type=video_status,
            contrast_enhance=contrast_enhance,
            xybin=xybin,
            medfilter=medfilter,
            gaussfilter=gaussian_filter,
            outdir=output_folder_name,
            scalebar=scalebar_on,
            topaz_denoise=topaz_denoise,
            denoise_with_cuda=denoise_with_cuda,
            im_type = output_type
        )  # output folder = output_folder+videos


def isvideo(dmfile):
    try:
        f = nci.dm.fileDM(dmfile)
        if f.zSize[1] > 1:
            return True
        else:
            return False
    except OSError as e:
        print(e)


def frames_processing(
    dm_frames, output_folder_name, xybin, medfilter, gaussian_filter, video_status
):
    dm_frames = group_frames(dm_frames)
    for vid in dm_frames:
        # if self.motioncor=='Off':
        print(dm_frames[vid])
        frames = dm_frames[vid]
        micrograph = Micrograph()
        micrograph.open_dm(frames[0])
        micrograph.add_frames(frames[1:])
        default_pipeline_class(
            micrograph,
            xybin=xybin,
            medfilter=medfilter,
            gaussfilter=gaussian_filter,
            outdir=output_folder_name,
        )


def get_files_from_pattern(pattern):
    """
    Imports all the files in the current directory that fits the defined pattern and returns them into lists of images, videos and digital micrograph frames
    The pattern allows for use of * for anything and ? for any single charactor, so for all tif files in the directory, one can use `*.tif` or give files with the same prefix but different number: filenumber00??.tif

    """

    dirfiles = os.listdir(".")
    files = []
    if "*" in pattern:
        pattern = pattern.replace("*", ".+")
        pattern = pattern.replace("?", ".")
        for file in dirfiles:
            if re.search(pattern, file):
                # print(file)
                files.append(file)
    im_files = []
    video_files = []
    frames = []
    # print(files)
    for file in files:
        if file[-4:-1] == ".dm":
            if isvideo(file):
                video_files.append(file)
            elif file[-9] == "-" and file[-13:-9].isdigit() and file[-8:-4].isdigit():
                frames.append(file)
            else:
                im_files.append(file)
        elif file[-4:] == ".avi" or file[-4:] == "mp4":
            video_files.append(file)
        elif file[-4:].lower() in [".tif", ".jpg", ".png", "tiff"]:
            im_files.append(file)
        else:
            print(
                "{} file not included as not a known image/video format, if this is unexpected please raise an issue on github".format(
                    file
                )
            )

    return im_files, video_files, frames


"""
            if '/' in outdir:
                if outdir.split('/')[-1] not in os.listdir('/'.join(outdir.split('/')[:-1])):
                    os.mkdir(outdir)
            elif outdir not in os.listdir('.') and outdir!='.' and outdir!='.':
                print(outdir)
                #print(os.listdir('.'))
                os.mkdir(outdir)

            if len(name.split('/'))>1:
                name=name.split('/')[:-1]+outdir+'/'+name
            else:
                name =outdir+'/'+name  
"""
