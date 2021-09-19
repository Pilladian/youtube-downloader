#!/usr/bin/python3

from eyed3.id3.frames import ImageFrame
from pytube import YouTube
from os import error
import subprocess
import argparse
import eyed3


def analyse_args(args):
    if (args.url == '' and args.file == '') or (args.url != '' and args.file != ''):
        raise ValueError('Please provide either a URL or a file containing URLs')
    
    if args.file != '':
        try:
            f = open(args.file)
            f.close()
        except IOError :
            raise IOError(f'File "{args.file}" not found.')

    if args.audio and args.video:
        raise ValueError('Please only specify either -a (audio only) or -v (video).')


def vpn_check():
    print(f' [!] Make sure, you\'re connected to your VPN')
    check = input(' [?] Continue (y/n): ')
    if check not in ['y', 'j', 'Y', 'J', 'yes', 'ja', 'YES', 'JA']:
        print(f' [ + ] Exited')
        exit(0)
    print("\033c\n", end="")


def print_args(args):
    if args.url != '':
        print(f' [ + ] Provided URL: \t{args.url}')

    elif args.file != '':
        print(f' [ + ] Provided File: \t\t{args.file}')

    if args.audio:
        print(f' [ + ] Download: \t\tAudio Only')
    elif args.video:
        print(f' [ + ] Download: \t\tVideo')

    print(f' [ + ] Storage Location: \t{args.location}\n')


def download(args):
    if args.file != '':
        with open(args.file, 'r') as url_file:
            urls = url_file.readlines()
            urls = [url for url in urls if url != '\n']
        urls = [url.split('\n')[0] for url in urls]
        for url in urls:
            if url[0] != '#':
                _download(url, args.location)
    else:
        _download(args.url, args.location)


def _download(url, dir):
    try:
        reference = YouTube(url)
        artists, title = extract_information(reference.title)
    except error as e:
        raise e
        
    tag = None

    if args.audio:
        streams = reference.streams.filter(only_audio=True)
        abr = 0
        for stream in streams:
            i, a = stream.itag, int(stream.abr.split('kbps')[0])
            if a > abr:
                tag, abr = i, a

    elif args.video:
        print('Not implemented yet')
        exit(1)

    stream = reference.streams.get_by_itag(tag)

    print(f' [ D ] {title}', end='\r')
    stream.download(dir)

    print(f' [ C ] {title}{" " * 10}', end='\r')
    if args.audio:
        subprocess.call(['ffmpeg', '-i', f'{dir}{stream.default_filename}', f'{dir}{title}.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.call(['rm', f'{dir}{stream.default_filename}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f' [ I ] {title}{" " * 10}', end='\r')
    audio = eyed3.load(f'{dir}{title}.mp3')
    if (audio.tag == None):
        audio.initTag()
    audio.tag.title = title
    audio.tag.artist = artists
    cover_file_name = f'{dir}{title} Cover.{reference.thumbnail_url.split(".")[-1]}'
    subprocess.call(['wget', reference.thumbnail_url, '-O', cover_file_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio.tag.images.set(3, open(cover_file_name, 'rb').read(), 'image/jpeg')
    subprocess.call(['rm', cover_file_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio.tag.save(version=eyed3.id3.ID3_V2_3)

    print(f' [ F ] {title}')


def extract_information(s):
    s = s.replace('–', '-')
    s = s.replace('/', '+')
    artists = s.split('-')[0]
    artists = artists.replace(' &', ',')
    artists = artists.replace(' x ', ', ')
    if 'ft.' in artists:
        feat = artists.split('ft. ')[1].split('-')[0].replace(' &', ',')
        artists = artists.split('ft.')[0]
        artists += 'ft. ' + feat
    elif 'ft' in artists:
        feat = artists.split('ft ')[1].split('-')[0].replace(' &', ',')
        artists = artists.split('ft')[0]
        artists += 'ft. ' + feat
    elif 'feat.' in artists:
        feat = artists.split('feat. ')[1].split('-')[0].replace(' &', ',')
        artists = artists.split('feat.')[0]
        artists += 'ft. ' + feat
    elif 'feat' in artists:
        feat = artists.split('feat ')[1].split('-')[0].replace(' &', ',')
        artists = artists.split('feat')[0]
        artists += 'ft. ' + feat
    elif 'ft.' in s:
        feat = s.split('ft. ')[1].split('(')[0].split(')')[0].replace(' &', ',')
        artists += 'ft. ' + feat
    elif 'ft' in s:
        feat = s.split('ft ')[1].split('(')[0].split(')')[0].replace(' &', ',')
        artists += 'ft. ' + feat

    title = s.split('-')[1].split('ft')[0].split('(')[0].split('[')[0]

    return artists, title

def main(args):
    
    analyse_args(args)
    vpn_check()
    print_args(args)

    download(args)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--url',
                        default='',
                        help='URL to Video, that will be downloaded')

    parser.add_argument('-f', '--file',
                        default='',
                        help='File of URLs that will be downloaded')

    parser.add_argument('-a', '--audio',
                        action='store_true',
                        help='Audio only Download')
    
    parser.add_argument('-v', '--video',
                        action='store_true',
                        help='Video Download')
    
    parser.add_argument('-l', '--location',
                        default='./',
                        help='Output Location')
    
    args = parser.parse_args()

    main(args)
    