from pathlib import Path
import shutil,subprocess,difflib,json
source=Path('/Users/rod.bondoc/workspace/buildtab')
fixture=Path('/tmp/buildtab-listing-2026.8.2')
assets=Path(__file__).resolve().parent.parent
assert not fixture.exists(), 'Use a fresh fixture directory'
fixture.mkdir()
for name in ['BuildTab','BuildTab.xcodeproj']:
 shutil.copytree(source/name,fixture/name)
(assets/'source/production-changes.patch').write_bytes(subprocess.check_output(['git','diff','HEAD'],cwd=source))
(assets/'source/source-revision.json').write_text(json.dumps({'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'working_tree_patch':'production-changes.patch','version':'2026.8.2','build':3},indent=2))
changes=[]
def edit(name,fn):
 p=fixture/name;old=p.read_text();new=fn(old);p.write_text(new)
 changes.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
edit('BuildTab.xcodeproj/project.pbxproj',lambda s:s.replace('app.buildtab.BuildTab','app.buildtab.listingdemo'))
edit('BuildTab/BuildTab.entitlements',lambda s:'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict/></plist>\n')
edit('BuildTab/Services/StoreService.swift',lambda s:s[:s.index('    private init() {')]+'''    private init() {
        purchasedProductIDs = [AppConstants.proProductID]
    }

'''+s[s.index('    func cleanup()'):])
app='''import SwiftUI
import SwiftData

@main
struct BuildTabApp: App {
    private let persistence = PersistenceController(inMemory: true)

    init() {
        UserDefaults.standard.set(true, forKey: AppConstants.UserDefaultsKeys.hasCompletedOnboarding)
        UserDefaults.standard.set("35", forKey: AppConstants.UserDefaultsKeys.defaultHourlyRate)
        ListingData.seed(persistence.container!.mainContext)
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .modelContainer(persistence.container!)
                .onAppear {
                    if UserDefaults.standard.bool(forKey: "screenshotLandscape") {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            for scene in UIApplication.shared.connectedScenes.compactMap({ $0 as? UIWindowScene }) {
                                scene.requestGeometryUpdate(.iOS(interfaceOrientations: .landscapeRight))
                            }
                        }
                    }
                }
        }
    }
}

@MainActor
enum ListingData {
    static var project: Project!
    static var route: String { UserDefaults.standard.string(forKey: "screenshotRoute") ?? "dashboard" }
    static var tab: Int {
        switch route {
        case "dashboard", "dark": return 0
        case "materials": return 2
        case "export": return 3
        default: return 1
        }
    }
    static func seed(_ context: ModelContext) {
        PreviewSampleData.createCategories().forEach { context.insert($0) }
        PreviewSampleData.createMaterialCategories().forEach { context.insert($0) }
        PreviewSampleData.createMaterials().forEach { context.insert($0) }
        let calendar = Calendar.current
        let date = calendar.date(from: DateComponents(year: 2026, month: 11, day: 4, hour: 12))!
        let desk = Project(name: "Walnut writing desk", category: "Woodworking", status: .inProgress,
            budgetTarget: 250, notes: "A quiet place to make something great.", createdAt: date,
            hourlyRateOverride: 35, overheadPercent: 10, targetMarginPercent: 30, salePrice: 425)
        context.insert(desk)
        let items: [(String, Decimal, Decimal, Decimal, String)] = [
            ("Walnut boards",168,4,3,"boards"), ("Hardwax oil",28,500,75,"ml"),
            ("Brass screws",12,100,24,"pcs"), ("Sandpaper",15,10,4,"sheets")]
        for (i,item) in items.enumerated() {
            context.insert(Expense(name:item.0,unitCost:item.1,quantityPurchased:item.2,quantityUsed:item.3,
                unit:item.4,category:["Woodworking","Paint & Finish","Hardware","Other"][i],supplier:"Workshop Supplies",
                purchaseDate:calendar.date(byAdding:.day,value: -i,to:date),project:desk))
        }
        for (hours,note,days) in [(Decimal(1.5),"Cut and join the desktop",2),(Decimal(1.25),"Shape the edges and sand",1),(Decimal(0.75),"Apply the first coat of oil",0)] {
            context.insert(TimeEntry(hours:hours,notes:note,date:calendar.date(byAdding:.day,value: -days,to:date)!,project:desk))
        }
        for (index,entry) in [("Leather card wallet","Leatherwork",Decimal(48)),("Garden planter","Woodworking",Decimal(76)),("Headphone stand","3D Printing",Decimal(18))].enumerated() {
            let p=Project(name:entry.0,category:entry.1,status:index==0 ? .complete : .inProgress,budgetTarget:entry.2*2,createdAt:calendar.date(byAdding:.day,value: -index-5,to:date)!)
            context.insert(p)
            context.insert(Expense(name:"Materials",unitCost:entry.2,quantityPurchased:1,quantityUsed:1,category:entry.1,purchaseDate:p.createdAt,project:p))
        }
        try! context.save()
        project=desk
    }
}

struct ListingProjectDestination: View {
    let project: Project
    @ViewBuilder var body: some View {
        switch ListingData.route {
        case "expense": ExpenseFormView(project:project,expense:project.expenses.first { $0.name=="Hardwax oil" })
        case "expenses": ExpensesListView(project:project)
        case "time": TimeEntriesListView(project:project)
        case "pricing": ProjectPricingView(project:project)
        case "spending": ProjectSpendingDetailView(project:project)
        default: ProjectDetailView(project:project)
        }
    }
}

'''
edit('BuildTab/App/BuildTabApp.swift',lambda s:app+s[s.index('struct PersistenceRootView:'):])
def content(s):
 s=s.replace('@SceneStorage("selectedTab") private var selectedTab = 0','@State private var selectedTab = ListingData.tab')
 s=s.replace('@State private var selectedProject: Project?','@State private var selectedProject: Project? = ListingData.project')
 s=s.replace('NavigationSplitView {','NavigationSplitView(preferredCompactColumn: .constant(.detail)) {')
 s=s.replace('ProjectDetailView(project: project)','ListingProjectDestination(project: project)')
 s=s.replace('                SettingsView()','                ExportView()')
 return s
edit('BuildTab/Views/ContentView.swift',content)
(assets/'source/offline-fixture.patch').write_text(''.join(changes))
print(fixture)
