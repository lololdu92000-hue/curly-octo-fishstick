set -e
cd "$(dirname "$0")"
ffmpeg -y -v error -framerate 24 -i frames/f%05d.jpg -c:v libx264 -preset slow -b:v 6000k -pass 1 -passlogfile p2 -an -f mp4 /dev/null
ffmpeg -y -v error -framerate 24 -i frames/f%05d.jpg -i music.wav -c:v libx264 -preset slow -b:v 6000k -maxrate 8000k -bufsize 12000k -pass 2 -passlogfile p2 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart sunvale-city-rp-trailer.mp4
ls -la sunvale-city-rp-trailer.mp4
