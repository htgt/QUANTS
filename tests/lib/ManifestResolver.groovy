import java.nio.file.Files

class ManifestResolver {
    static File resolveSheet(def projectDir, String manifestFileName) {
        String projectDirPath = projectDir.toString()
        File manifest = new File("${projectDirPath}/tests/manifests/${manifestFileName}")
        String raw = manifest.text

        String resolved = raw.replace(
            "tests/quants-data",
            "${projectDirPath}/tests/quants-data"
        )

        File tmpDir = Files.createTempDirectory("nf-test-").toFile()
        tmpDir.deleteOnExit()

        File resolvedSheet = new File(tmpDir, manifestFileName.replace(".csv", ".resolved.csv"))
        resolvedSheet.text = resolved
        resolvedSheet.deleteOnExit()

        return resolvedSheet
    }
}