#pragma once

#include <QMap>
#include <QObject>
#include <QString>
#include <QStringList>
#include <QVariant>
#include <QVariantMap>
#include <QVariantList>


class ParameterObject : public QObject {
    Q_OBJECT
public:
    explicit ParameterObject();
    QString name;
    QString description;
    QString defaultValue;
    QStringList allowedValues;
};


class ServiceObject : public QObject {
    Q_OBJECT
public:
    explicit ServiceObject(const QString &);

    QString name;
    QString summary;
    QString description;
    QMap<QString, std::shared_ptr<ParameterObject>> parameters;
private:
    std::shared_ptr<ParameterObject> getParameterObject(const QString & name);
};


class MyApp : public QObject
{
    Q_OBJECT

public:
    explicit MyApp(const QString & directory, const QString & service_file);

public slots:
    bool save(const QString &content);

    QString getServiceDefaultParam(const QString &name);

    QString getParamDefaultValue(const QString &name,
                                 const QString &param);

    QStringList getServices();

    QStringList getParamValues(const QString &name,
                                const QString &param);

    QStringList getServiceParams(const QString &name);

    QString showService(const QString &selectedText);

    QString showParam(const QString &service,
                      const QString &text);

private:
    QMap<QString, std::shared_ptr<ServiceObject>> services;
    QString service_file;
};

