import Foundation

guard CommandLine.arguments.count > 1 else {
    FileHandle.standardError.write("usage: AppleEventKitHost <program> [args...]\n".data(using: .utf8)!)
    exit(64)
}

let child = Process()
child.executableURL = URL(fileURLWithPath: CommandLine.arguments[1])
child.arguments = Array(CommandLine.arguments.dropFirst(2))
do {
    try child.run()
} catch {
    FileHandle.standardError.write("AppleEventKitHost: \(error)\n".data(using: .utf8)!)
    exit(70)
}
child.waitUntilExit()
exit(child.terminationStatus)
