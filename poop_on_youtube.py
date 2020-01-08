import random
from pytube import YouTube
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import glob
from moviepy.editor import *
import moviepy.video.fx.all as vfx
import numpy as np
import webbrowser
from tqdm import tqdm

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="US"
    )
    response = request.execute()

    with open('mostpopular.json', 'w') as file:
        file.write(json.dumps(response))
    print('Parsing Response')


def randomizeClip(clip, x):
    try:
        if x == "accel_decel":
            dur = random.randint(0, np.floor(clip.duration) * 2)
            if dur == 0:
                dur == None
            a = random.uniform(-1, 1)
            s = random.uniform(0, 100)
            return vfx.accel_decel(clip, new_duration=dur, abruptness=a, soonness=s)
        elif x == "blackwhite":
            return vfx.blackwhite(clip)
        elif x == "blink":
            do = random.randint(0, 10)
            doff = random.randint(0, 10)
            return vfx.blink(clip, d_on=do, d_off=doff)
        elif x == "colorx":
            factor = random.randint(1, 1000)
            return vfx.colorx(clip, factor=factor)
        elif x == "crop":
            return clip
        elif x == "even_size":
            return vfx.even_size(clip)
        elif x == "fadein":
            d = random.randint(0, np.floor(clip.duration))
            i = random.random()
            return vfx.fadein(clip, d, i)
        elif x == "fadeout":
            d = random.randint(0, np.floor(clip.duration))
            i = random.random()
            return vfx.fadeout(clip, d, i)
        elif x == "freeze":
            t = random.randint(0, np.floor(clip.duration))
            td = random.randint(0, np.floor(clip.duration))
            return vfx.freeze(clip, t=t, total_duration=td)
        elif x == "freeze_region":
            return vfx.freeze_region(clip, mask=ImageClip(np.random.rand(clip.size[0], clip.size[1]), ismask=True))
        elif x == "gamma_corr":
            g = random.randint(0, 10)
            return vfx.gamma_corr(clip, g)
        elif x == "headblur":
            pass
        elif x == "invert_colors":
            return vfx.invert_colors(clip)
        elif x == "loop":
            ls = random.randint(0, 10)
            return vfx.loop(clip, n=ls)
        elif x == "lum_contrast":
            return vfx.lum_contrast(clip)
        elif x == "make_loopable":
            ls = random.randint(0, np.floor(clip.duration))
            return vfx.make_loopable(clip, ls)
        elif x == "margin":
            s = clip.size(0) / random.randint(2, 10)
            o = random.random()
            return vfx.margin(clip, left=s, right=s, top=s, bottom=s, opacity=o)
        elif x == "mask_and":
            return vfx.mask_and(clip, ImageClip(np.random.rand(clip.size[0], clip.size[1]), ismask=True))
        elif x == "mask_color":
            thr = random.random()
            return vfx.mask_color(clip, thr=thr)
        elif x == "mask_or":
            return vfx.mask_or(clip, ImageClip(np.random.rand(clip.size[0], clip.size[1]), ismask=True))
        elif x == "mirror_x":
            return vfx.mirror_x(clip)
        elif x == "mirror_y":
            return vfx.mirror_y(clip)
        elif x == "painting":
            s = random.uniform(0, np.floor(clip.duration))
            b = random.randint(0, 100)/1000
            return vfx.painting(clip, saturation=s, black=b)
        elif x == "resize":
            u = random.random()
            return vfx.resize(clip, u)
        elif x == "rotate":
            u = random.uniform(0, 360)
            return vfx.rotate(clip, u)
        elif x == "scroll":
            return clip
        elif x == "speedx":
            u = random.uniform(0, 100)
            return vfx.speedx(clip, u)
        elif x == "supersample":
            g = random.randint(0, 10)
            d = int(clip.duriation/2)
            return vfx.supersample(clip, d, g)
        elif x == "time_mirror":
            return vfx.time_mirror(clip)
        elif x == "time_symmetrize":
            return vfx.time_symmetrize(clip)
        else:
            return clip
    except:
        return clip


def getfunctions():
    from inspect import getmembers, isfunction
    import moviepy.video.fx.all as vfx

    functions_list = [o for o in getmembers(vfx) if isfunction(o[1])]
    return list(functions_list)


def poop():
    funcs = getfunctions()
    videos = glob.glob("*.mp4")

    for v in tqdm(videos,desc='Video'):
        print(f'\n{v}')
        clip = VideoFileClip(v)
        segs = np.linspace(0, clip.duration, random.randint(1, np.floor(clip.duration)))
        #segs = [0,20,60,150,300,500,600,1000,clip.duration]
        clips = []
        for x in tqdm(range(1, len(segs)), desc='Subclip', leave=False):
            c = clip.subclip(segs[x - 1], segs[x])
            sampling = random.choices(funcs, k=random.randint(1, np.ceil(len(funcs) / 2)))
            for x, f in sampling:
                c = randomizeClip(c, x)

            if c is not None:
                if c.duration is not None:
                    if c.audio is not None:
                        clips.append(c)
                    else:
                        print('\nI got no audio bro.................')
                else:
                     print('\nMan this package is kinda poopy.')
            else:
                print('\nHello error. Goodbye Segment.')
         try:
            final = CompositeVideoClip(clips)
            final.write_videofile(f"{v[:-4]}--pooped.mp4", write_logfile=True,
                                preset='ultrafast',
                                temp_audiofile='temp-audio.mp3',
                                audio=True,
                                remove_temp=True)
          except:
             for x in range(0, 100):
                 print('\n:(')
             webbrowser.open_new('https://www.youtube.com/watch?v=IMYbjyKWaak')


def parse_and_download():
    with open('mostpopular.json', 'r') as file:
        pop = json.load(file)

    for x in pop['items']:
        try:
            print(f"Downloading: {x['snippet']['title']} (https://www.youtube.com/watch?v={x['id']})")
            YouTube(f'http://youtube.com/watch?v={x["id"]}').streams.first().download()
        except:
            print('lul download failed u sux')

if __name__ == "__main__":
    main()
    parse_and_download()
    poop()
