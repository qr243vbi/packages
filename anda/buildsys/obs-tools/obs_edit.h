#pragma once

#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QObject>
#include <QMessageBox>



class ServiceListener: public QObject {
    Q_OBJECT

signals:
    void addServices(const QVariantList &services);

public slots:
    void showMessage(const QString &title, const QString &text);
};
