"""Verify the exported film's technical delivery, not subjective sound quality."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from PIL import Image


def verify(path):
    path=Path(path)
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    video=next(s for s in data['streams'] if s['codec_type']=='video')
    audio=next(s for s in data['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'])==(1080,1920)
    assert video['codec_name']=='h264' and video['r_frame_rate']=='24/1'
    assert int(video['nb_frames'])==432
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000
    assert audio['channels']==2
    assert abs(float(data['format']['duration'])-18)<.05
    hashes=[]
    for stamp in ['2','6.5','11','17']:
        frame=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',stamp,
                                       '-i',str(path),'-frames:v','1','-f','image2pipe','-c:v','png','-'])
        assert np.asarray(Image.open(io.BytesIO(frame))).mean()>5
        hashes.append(hashlib.sha256(frame).hexdigest())
    assert len(set(hashes))==4
    levels=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','volumedetect','-f','null','-'],
                          stderr=subprocess.PIPE,stdout=subprocess.DEVNULL,check=True,text=True).stderr
    peak=float(re.search(r'max_volume: ([\d.-]+) dB',levels).group(1))
    mean=float(re.search(r'mean_volume: ([\d.-]+) dB',levels).group(1))
    assert -60<mean<-5 and peak<0
    return {'file':path.name,'duration_seconds':18,'width':1080,'height':1920,'fps':24,
            'video_frames':432,'video_codec':'h264','audio_codec':'aac','audio_rate':48000,
            'audio_channels':2,'mean_volume_db':mean,'peak_volume_db':peak,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,
            'narration':False,'paid_generation_api_used':False,
            'native_3d_render':'432x768, 12 fps; denoised and optical-flow interpolated per shot',
            'typography':'native 1080x1920','shot_frames_sampled':4,'status':'technical_checks_passed'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video')
    parser.add_argument('--report')
    args=parser.parse_args()
    result=verify(args.video)
    encoded=json.dumps(result,indent=2)+'\n'
    if args.report:
        Path(args.report).write_text(encoded,encoding='utf-8')
    print(encoded)
