import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.ApplicationWindow {
    Kirigami.FormLayout {
        anchors.fill: parent

        Controls.TextField {
            Kirigami.FormData.label: "First name:"
        }
        Controls.TextField {
            Kirigami.FormData.label: "Middle name:"
            Kirigami.FormData.checkable: true
            enabled: Kirigami.FormData.checked
        }
        Controls.TextField {
            Kirigami.FormData.label: "Last name:"
        }
    }
}
