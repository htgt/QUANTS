//
// derive deterministic local filename from an iRODS path
//

def local_file_name(String irodsPath) {
    def path = irodsPath.toString()
    return path
        .replaceFirst('^/', '')              
        .replaceAll('[^A-Za-z0-9._-]', '_')  
        .replaceAll('_+', '_')               
        .replaceAll('^_+|_+$', '')           
}
