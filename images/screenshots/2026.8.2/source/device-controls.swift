import AppKit
import ApplicationServices
let processID = pid_t(ProcessInfo.processInfo.environment["DEVICE_HUB_PID"]!)!
NSRunningApplication(processIdentifier: processID)?.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])
sleep(1)
let app = AXUIElementCreateApplication(processID)
func attr(_ e: AXUIElement, _ key: String) -> AnyObject? { var value: CFTypeRef?; guard AXUIElementCopyAttributeValue(e, key as CFString, &value) == .success else { return nil }; return value }
func walk(_ e: AXUIElement, _ depth: Int) {
 let role = attr(e,"AXRole") as? String ?? ""
 let title = attr(e,"AXTitle") as? String ?? ""
 let desc = attr(e,"AXDescription") as? String ?? ""
 let value = attr(e,"AXValue") as? String ?? ""
 if CommandLine.arguments.count == 1 { print(role + " " + title + " " + desc + " " + value) }
 if role == "AXStaticText", CommandLine.arguments.count > 1, value == CommandLine.arguments[1] {
 let cell = attr(e,"AXParent") as! AXUIElement
 let row = attr(cell,"AXParent") as! AXUIElement
 print("Selecting",value,AXUIElementSetAttributeValue(row,"AXSelected" as CFString,kCFBooleanTrue).rawValue);exit(0)
 }
 if role == "AXButton", CommandLine.arguments.count > 1, desc == CommandLine.arguments[1] {
 print("Pressing " + desc); print(AXUIElementPerformAction(e, "AXPress" as CFString).rawValue); exit(0)
 }
 if depth < 45 { for child in attr(e,"AXChildren") as? [AXUIElement] ?? [] { walk(child, depth+1) } }
}
walk(app, 0)
