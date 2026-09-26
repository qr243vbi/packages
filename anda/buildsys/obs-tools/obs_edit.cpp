#include "obs_edit.h"


void ServiceListener::showMessage(const QString &title, const QString &text)
{
    QMessageBox msgBox;
    msgBox.setWindowTitle(title);
    msgBox.setText(text);
    msgBox.setStandardButtons(QMessageBox::Ok);
    msgBox.exec();
}

extern "C"{
    int obs_edit(int argc, char ** argv, QObject * app_instance, const QVariantList & list);
}


int obs_edit(int argc, char ** argv, QObject * app_instance, const QVariantList & list){
    QApplication app(argc, argv);
    qDebug () << "EDIT";
    QQmlApplicationEngine engine;
    qDebug() << "SECOND";

    auto app_listener = new ServiceListener();
    qDebug() << "FUNNY";
    engine.rootContext()->setContextProperty("obs", app_instance);
    engine.rootContext()->setContextProperty("messageDialog", app_listener);
    engine.load(QUrl(QStringLiteral("qrc:/obs_edit.qml")));

    if (engine.rootObjects().isEmpty()){
        qDebug() << "FAILURE";
    }

    qDebug() << list;
    emit app_listener->addServices(list);

    return app.exec();
}
