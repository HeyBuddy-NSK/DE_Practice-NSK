from config import Config
from main import download_file, file_unzip


def main():
    # for uri in Config.DOWNLOAD_URI:
    #     pass
    # downloading one file
    url = Config.DOWNLOAD_URI[0]
    download_file_path = download_file(url)
    if download_file_path:
        print("Download Successful!.")
        if file_unzip(download_file_path):
            print('extraction complete!.')
    else:
        print("Download Failed")

if __name__=='__main__':
    main()