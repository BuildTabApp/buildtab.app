import Foundation
import Vision
import AppKit
let paths = CommandLine.arguments.dropFirst()
for path in paths {
 let url = URL(fileURLWithPath: path)
 let request = VNRecognizeTextRequest()
 request.recognitionLevel = .accurate
 request.recognitionLanguages = ["es-ES", "en-US"]
 do {
  try VNImageRequestHandler(url: url).perform([request])
  let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
  let data = try JSONSerialization.data(withJSONObject: ["file": path, "text": lines], options: [.sortedKeys])
  print(String(data: data, encoding: .utf8)!)
 } catch { fputs("\(path): \(error)\n", stderr); exit(1) }
}
