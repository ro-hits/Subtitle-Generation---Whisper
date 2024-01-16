import os
import ffmpeg
import whisper
import argparse


def convert_time(time):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((time - int(time)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def get_subtitle(video_path):

    model = whisper.load_model("small")

    # Extract audio from the video file using FFmpeg
    audio_path = "audio.wav"
    (
        ffmpeg.input(video_path)
        .output(audio_path, format="wav", acodec="pcm_s16le", ac=1, ar=16000)
        .overwrite_output()
        .run()
    )

    result = model.transcribe(audio_path)

    video_filename = os.path.splitext(os.path.basename(video_path))[0]

    subtitle_path = f"{video_filename}.srt"

    with open(subtitle_path, "w") as f:
        for i, caption in enumerate(result["segments"]):
            start_time = convert_time(int(caption["start"]))
            end_time = convert_time(int(caption["end"]))
            text = caption["text"]
            f.write(f"{i + 1}\n{start_time} --> {end_time}\n{text}\n\n")

    # Remove the temporary audio file
    os.remove(audio_path)
    print("Subtitle saved as", subtitle_path)

def main():
    parser = argparse.ArgumentParser(description="Generate subtitles for your video")
    parser.add_argument("--input", help="Path to the input video file", required=True)
    args = parser.parse_args()

    video_path = args.input
    get_subtitle(video_path)

if __name__ == '__main__':
    main()