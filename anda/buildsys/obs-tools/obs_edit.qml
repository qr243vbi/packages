
import QtQuick 6.10
import QtQuick.Controls 6.10
import QtQuick.Dialogs 6.10


ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Qt Quick Vertical Layout Example"
    id: appWindow;



    function getXml(){
        var str = "<services>\n"
        var services_count = column.count
        var services_index = 0
        while (services_index < services_count){
            var name = (column.itemAtIndex(services_index).children[0].children[1].children[0].text)
            var mode = (column.itemAtIndex(services_index).children[0].children[3].editText)
            str += " <service name=" + JSON.stringify(name)
            if (mode != "default") {
                str += " mode=" + JSON.stringify(mode)
            }
            str += ">\n"
            var params_index = 0
            var params_count = 0;
            params_count = column.itemAtIndex(services_index).children[2].count
            while (params_index < params_count){
                var param = (column.itemAtIndex(services_index).children[2].itemAtIndex(params_index).children[1].children[0].text)
                var value = (column.itemAtIndex(services_index).children[2].itemAtIndex(params_index).children[3].editText)
                str += "  <param name=" + JSON.stringify(param) + ">" + value + "</param>\n"
                params_index += 1
            }
            str += " </service>\n"
            services_index += 1
        }
        str += "</services>\n"
        return str
    }

    function generateUniqueId() {
        return Date.now() * 256 +  Math.floor(Math.random() * 256);
    }

    ListModel {
        id: p1model
    }
/*
    MessageDialog {
        id: messageDialog
        title: "Selection"
    }*/

    Connections {
        target: messageDialog
        function onAddServices(message) {
            console.log(message)
            for (var i of message){
                var id = generateUniqueId()
                var value = JSON.stringify(i[2])
                p1model.append({text: i[0], uuid: "A" + id, defval: i[1], values: value})
            }
        }
    }

    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }

    property var selectedText: ""

    ScrollView {
        anchors.fill: parent

        id: scroll
        Column{
            x: 10
            width: scroll.width - 30
            spacing: 17

            Row{
                width: parent.width   // Set width to 90% of the parent
                anchors.right: parent.right;
                x: 0
                spacing: 10
                ComboBox {
                    height: 30;
                    width: parent.width - 40 - 40
                    id: serviceList
                    editable: true  // Make the ComboBox editable
                    model: ListModel{}
                    onFocusChanged: {
                        if (focus){
                            this.model.clear()
                            for (var key of obs.getServices()){
                                this.model.append({text: key})
                            }
                        } else {
                            selectedText = this.editText
                        }
                    }
                }

                Button {
                    text: "?"
                    width: 30;
                    height: 30;
                    onClicked: {
                        messageDialog.showMessage(selectedText, obs.showService(selectedText))
                    }
                }

                Button {
                    text: "+"
                    width: 30;
                    height: 30;
                    onClicked: {
                        var id = generateUniqueId()
                        p1model.append({text: selectedText, uuid: "A" + id, defval: "default", values: '[]'})
                    }
                }
            }


            ListView {
                id: column
                width: parent.width - 24
                model: p1model

                height: contentHeight
                spacing: 22
                x: 12

                delegate:
                Column {
                    property var uniqueId: uuid
                    property var serviceName: text
                    property var selectedParam: undefined
                    property var parentIndex: index
                    property var mode: defval
                    width: parent.width  // Set width to 90% of the parent
                    anchors.right: parent.right;

                    spacing: 10

                    Component.onCompleted: {
                        console.log("service ID is: " + uniqueId)
                        var params = JSON.parse(values)
                        var model = this.children[2].model
                        for (var p of params){
                            var name = p[0]
                            var text = p[1]
                            var id = generateUniqueId()
                            model.append({name: name, uuid: id, defval: text})
                        }
                        var combobox = this.children[0].children[3]
                        let index = combobox.model.indexOf(defval)
                        if (index !== -1) {
                            combobox.currentIndex = index;
                        }
                    }

                    Column{



                        width: parent.width  // Set width
                        anchors.right: parent.right;

                        Text {
                            text: "Service"  // The text displayed in the label
                            font.pointSize: 12
                            height: 20
                            color: myPalette.text   // Text color
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Row{
                            width: parent.width   // Set width to 90% of the parent
                            anchors.right: parent.right;
                            spacing: 10
                            x: 0

                            TextField {
                                height: 30;
                                width: parent.width - 40 - 40 - 40
                                text: serviceName
                                onFocusChanged: {
                                    if (!focus){
                                        serviceName = this.text
                                    }
                                }
                            }

                            Button {
                                text: "⬇️"
                                width: 30
                                height: 30;
                                onClicked: {
                                    p1model.move(index, index + 1, 1)
                                }
                            }

                            Button {
                                text: "⬆️"
                                width: 30;
                                height: 30;
                                onClicked: {
                                    p1model.move(index, index - 1, 1)
                                }
                            }

                            Button {
                                text: "-"
                                width: 30
                                height: 30
                                onClicked: {
                                    p1model.remove(index)
                                }
                            }
                        }
                        Text {
                            text: "Service Mode"  // The text displayed in the label
                            font.pointSize: 11
                            height: 20
                            color: myPalette.text  // Text color
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        ComboBox {
                            height: 30;
                            width: parent.width
                            editable: false  // Make the ComboBox editable
                            model: ["default", "buildtime", "localonly", "trylocal", "manual", "disabled", "serveronly"]
                            onFocusChanged: {
                                if (!focus){
                                    selectedText = this.editText
                                }
                            }
                        }
                    }

                    Column{
                        width: parent.width  // Set width
                        anchors.right: parent.right;

                        Text {
                            text: "Service Parameters"  // The text displayed in the label
                            font.pointSize: 11
                            height: 20
                            color: myPalette.text   // Text color
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Row{
                            width: parent.width   // Set width to 90% of the parent ⬆️
                            anchors.right: parent.right
                            x: 0
                            spacing: 10
                            ComboBox {
                                height: 30;
                                width: parent.width - 40 - 40
                                editable: true  // Make the ComboBox editable
                                model: ListModel{}
                                onFocusChanged: {
                                    if (focus){
                                        this.model.clear();
                                        for (var key of obs.getServiceParams(serviceName)){
                                            this.model.append({text: key})
                                        }
                                    } else {
                                        selectedParam = this.editText
                                    }
                                }
                            }

                            Button {
                                text: "?"
                                width: 30;
                                height: 30;
                                onClicked: {
                                    messageDialog.showMessage(selectedParam,
                                        obs.showParam(serviceName, selectedParam))
                                }
                            }

                            Button {
                                text: "+"
                                width: 30;
                                height: 30;
                                onClicked: {
                                    var param = selectedParam
                                    if (param == undefined){
                                        param = obs.getServiceDefaultParam(serviceName)
                                    }
                                    var id = generateUniqueId()
                                    var defval1 =  obs.getParamDefaultValue(serviceName, param);
                                    var combobox = this.parent.parent.parent.children[2]
                                    combobox.model.append({
                                        name: param, uuid: "A" + id, defval: defval1})
                                }
                            }
                        }
                    }


                    ListView {
                        id: column
                        width: parent.width

                        height: contentHeight
                        spacing: 10
                        model: ListModel{}

                        delegate: Column{
                            property var paramName: name
                            property var uniqueId: uuid
                            property var paramValue: defval
                            width: parent.width  // Set width to 90% of the parent
                            anchors.right: parent.right;


                            Component.onCompleted: {
                                this.children[3].editText = paramValue
                                console.log("param ID is: " + uniqueId)
                            }

                            spacing: 5
                            Text {
                                text: "Parameter"  // The text displayed in the label
                                font.pointSize: 11
                                height: 20
                                color: myPalette.text   // Text color
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            Row{
                                width: parent.width   // Set width to 90% of the parent
                                anchors.right: parent.right;
                                spacing: 10
                                x: 0

                                TextField {
                                    height: 30;
                                    width: parent.width - 40 - 40 - 40
                                    text: paramName
                                    onFocusChanged: {
                                        if (!focus){
                                            paramName = this.text
                                        }
                                    }
                                }

                                Button {
                                    text: "⬇️"
                                    width: 30
                                    height: 30;
                                    onClicked: {
                                        this.parent.parent.parent.parent.model.move(index, index + 1, 1)
                                    }
                                }

                                Button {
                                    text: "⬆️"
                                    width: 30;
                                    height: 30;
                                    onClicked: {
                                        this.parent.parent.parent.parent.model.move(index, index - 1, 1)
                                    }
                                }

                                Button {
                                    text: "-"
                                    width: 30
                                    height: 30
                                    onClicked: {
                                        this.parent.parent.parent.parent.model.remove(index)
                                    }
                                }
                            }
                            Text {
                                text: "Value"  // The text displayed in the label
                                font.pointSize: 11
                                height: 20
                                color: myPalette.text  // Text color
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            ComboBox {
                                height: 30;
                                width: parent.width
                                id: comboBoxValue
                                editable: true  // Make the ComboBox editable
                                model: ListModel{}

                                onFocusChanged: {
                                    if (!focus){
                                        paramValue = this.editText
                                    } else {
                                        var serviceName = this.parent.parent.parent.parent.serviceName
                                        var list = obs.getParamValues(serviceName, paramName)
                                        this.model.clear()
                                        for (var text of list){
                                            this.model.append({text: text})
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Button {
                text: "Save"
                width: parent.width - 20;
                x: 10
                height: 30;
                onClicked: {
                    console.log(obs.save(getXml()))
                }
            }
        }
    }
}
