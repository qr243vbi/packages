#include <iostream>
#include <qobject.h>
#include <string>
#include <QFile>
#include <QDebug>
#include <QDir>
#include <QCommandLineParser>
#include <QCommandLineOption>
#include <functional>
#include <QIODevice>
#include <QDomDocument>
#include <QDomNodeList>
#include <QFileInfo>
#include <iostream>
#include <QRandomGenerator>
#include <QProcess>
#include <filesystem>
#include "obs_tools.h"
#include <QString>
#include <QRegularExpression>
#include <dlfcn.h>


namespace fs = std::filesystem;
using namespace std;

const char * obs_path = "/usr/lib/obs/service";
inline bool verbose_mode = false;

inline void putenv(const char * env, QByteArrayView value){
    if (qEnvironmentVariableIsEmpty(env)) qputenv(env, value);
}

QString dictToYaml(const QVariantMap &data,
                   const QStringList &skip = {},
                   int indent = 0,
                   bool skipEmpty = true,
                   int step = 2)
{
    QString yaml;

    for (auto it = data.constBegin(); it != data.constEnd(); ++it) {
        const QString &key = it.key();
        const QVariant &value = it.value();

        // Skip keys in skip list
        if (skip.contains(key))
            continue;

        // Skip empty values
        if (skipEmpty) {
            if (value.typeId() == QMetaType::QString && value.toString().isEmpty())
                continue;
            if (value.typeId() == QMetaType::QVariantMap && value.toMap().isEmpty())
                continue;
            if (value.typeId() == QMetaType::QVariantList && value.toList().isEmpty())
                continue;
        }

        yaml += QString(indent, ' ') + key + ": ";

        // Dictionary
        if (value.typeId() == QMetaType::QVariantMap) {
            yaml += "\n";
            yaml += dictToYaml(value.toMap(), skip, indent + step, skipEmpty, step);
        }

        // List
        else if (value.typeId() == QMetaType::QVariantList) {
            yaml += "\n";
            for (const QVariant &item : value.toList()) {
                if (item.typeId() == QMetaType::QVariantMap) {
                    yaml += QString(indent + step, ' ') + "-\n";
                    yaml += dictToYaml(item.toMap(), skip,
                                       indent + step + step,
                                       skipEmpty,
                                       step);
                } else {
                    yaml += QString(indent + step, ' ')
                    + "- "
                    + item.toString()
                    + "\n";
                }
            }
        }

        // String
        else if (value.typeId() == QMetaType::QString) {
            QString str = value.toString();
            int i = 0, u = str.size() - 1;
            while (str[i] == '\n' && i <= u) i ++;
            while (str[u] == '\n' && u >= i) u --;
            if (i > u) str = "";
            else str = str.slice(i, u - i + 1);
            if (str.contains('\n')) {
                yaml += "|\n";
                yaml += QString(indent + step, ' ')
                + str.replace("\n", "\n" + QString(indent + step, ' '))
                + "\n";
            } else {
                yaml += str + "\n";
            }
        }

        // Other types (int, bool, double, etc.)
        else {
            yaml += value.toString() + "\n";
        }
    }

    return yaml;
}


void extractCpioFromStream(const QString &archivePath) {
    // Prepare the command
    QStringList args;
    args << "-idmu" << "--sparse" << "--no-absolute-filenames" << "--force-local";

    // Create a QProcess
    QProcess process;

    // Set the working directory to the parent directory of the archive
    QDir parentDir = QFileInfo(archivePath).dir(); // Get the parent directory
    process.setWorkingDirectory(parentDir.absolutePath());

    // Open the archive file as input
    QFile archiveFile(archivePath);
    if (!archiveFile.open(QIODevice::ReadOnly)) {
        qDebug() << "Could not open archive file:" << archiveFile.errorString();
        return;
    }
    // Connect the output signal
    QObject::connect(&process, &QProcess::readyReadStandardOutput, [&process]() {
        QString output(process.readAllStandardOutput());
        cout << output.toStdString();
    });

    // Connect the error signal
    QObject::connect(&process, &QProcess::readyReadStandardError, [&process]() {
        QString errorOutput(process.readAllStandardError());
        cerr << errorOutput.toStdString();
    });

    // Start the cpio process
    process.start("cpio", args);

    if (!process.waitForStarted()) {
        qDebug() << "Failed to start cpio:" << process.errorString();
        return;
    }

    // Write the file data to the cpio process
    process.write(archiveFile.readAll());
    archiveFile.close();
    process.closeWriteChannel(); // Indicate that no more data will be sent

    // Wait for the process to finish
    process.waitForFinished(0xFFFFFFFF);
}

void print(const QString & value){
    if (verbose_mode) {
        qDebug() << value;
    }
}

QString generateRandomString(int length) {
    const QString chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    QString result;

    // Use QRandomGenerator to generate random indexes
    for (int i = 0; i < length; ++i) {
        int index = QRandomGenerator::global()->bounded(chars.size());
        result.append(chars[index]);
    }

    return result;
}

struct Parameter{
    QString name;
    QString text;
    Parameter(const QString &name, const QString& value){
        this->name = name;
        this->text = value;
    }
};

int runProcess(const QString &program, const QStringList &arguments, const QString &workingDirectory) {
    QProcess process;
    process.setWorkingDirectory(workingDirectory);

    process.setProcessChannelMode(QProcess::ForwardedChannels);

    // Start the process
    process.start(program, arguments);

    // Check if the process started successfully
    if (!process.waitForStarted()) {
        return -1; // Return -1 to indicate an error in starting
    }

    // Wait for the process to finish
    process.waitForFinished(0xFFFFFFFF);

    qDebug() << "";
    qDebug() << "###########################################";

    // Return the exit code of the process
    return process.exitCode();
}

struct Global {
    QString apiurl, project, package;
};

struct Service{
    QString name;
    QString path;
    QList<Parameter> paramList;
    std::shared_ptr<Global> globalapi;

    Service(const QString & path, QList<Parameter> paramList, const QString &name){
        this->name = name;
        this->path = path;
        this->paramList = paramList;
    }

    int Run(const QString & workdir, const QString & outdir){
        QStringList arguments;
        for (Parameter par: paramList){
            arguments << "--" + par.name << par.text;
        }
        arguments << "--outdir" << outdir;
        qDebug() << "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^";
        qDebug() << "WORKDIR" << workdir;
        qDebug() << "PATH" << path ;
        qDebug() << "ARGS" << arguments;
        qDebug() << "-------------------------------------------";
        return runProcess(path, arguments, workdir);
    }

    int Run(const QDir & workdir, const QDir & outdir){
        return Run(workdir.absolutePath(), outdir.absolutePath());
    }
};


QFileInfoList getFileList(const QDir & dir){
    return  dir.entryInfoList(
        QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot
    );
}

QFileInfoList getFileList(const QString & dirPath){
    QDir dir(dirPath);
    return  getFileList(dir);
}

QStringList getPackages(const QString & service_filepath, const QString & repolist_filepath){
    QStringList ll;
    if (!service_filepath.isEmpty()){
        QDomDocument service;
        QFile service_file(service_filepath);
        if (service_file.open(QIODevice::ReadOnly)) {
            service.setContent(&service_file);
            QDomNodeList items = service.elementsByTagName("service");
            for (auto serv : items) {
                QDomElement e = serv.toElement();
                QString name;
                print(
                    "name = " + (name = e.attribute("name"))
                );
                ll << "obs-service-" + name;
            }
        }
    }
    if (!repolist_filepath.isEmpty()){
        QDomDocument repolist;
        QFile repolist_file(repolist_filepath);

        if (repolist_file.open(QIODevice::ReadOnly)) {
            repolist.setContent(&repolist_file);
            QDomNodeList items = repolist.elementsByTagName("pkg");
            for (auto serv : items) {
                QDomElement e = serv.toElement();
                QString name;
                print(
                    "name = " + (name = e.text())
                );
                ll << name;
            }
        }
    }
    return ll;
}


QStringList getRepos(const QString & repolist_filepath){
    QStringList ll;
    if (!repolist_filepath.isEmpty()){
        QDomDocument repolist;
        QFile repolist_file(repolist_filepath);

        if (repolist_file.open(QIODevice::ReadOnly)) {
            repolist.setContent(&repolist_file);
            QDomNodeList items = repolist.elementsByTagName("url");
            for (auto serv : items) {
                QDomElement e = serv.toElement();
                QString name;
                print(
                    "url = " + (name = e.text())
                );
                ll << name;
            }
        }
    }
    return ll;
}

enum ServiceTag{
    ServiceSummary,
    ServiceDescription,
    ParameterDescription,
    AllowedValue,
    DefaultValue
};

void DescriptionParse(const QString & filepath, std::function<void(const QString&, const QString&, int)> func){
    QDomDocument doc;
    QFile file(filepath);
    if (!file.open(QIODevice::ReadOnly)) {
        print("cannot open file");
        return;
    }
    if (!doc.setContent(&file)) {
        print("invalid XML");
        file.close();
        return;
    }
    file.close();

    QDomElement root = doc.documentElement();
    if (root.tagName() == "service"){
        func(root.attribute("name"), root.firstChildElement("summary").text(), ServiceTag::ServiceSummary);
        func(root.attribute("name"), root.firstChildElement("description").text(), ServiceTag::ServiceDescription);
        for (QDomNode serv : root.elementsByTagName("parameter")) {
            QDomElement parameter = serv.toElement();

            QString name = parameter.attribute("name");
            for (QDomNode serv1: parameter.childNodes()){
                if (!serv1.isElement()){
                    continue;
                }
                QDomElement element = serv1.toElement();
                QString type = element.tagName();
                int i = 0;
                if (type == "allowedvalue"){
                    i = ServiceTag::AllowedValue;
                } else if (type == "description"){
                    i = ServiceTag::ParameterDescription;
                } else if (type == "default"){
                    i = ServiceTag::DefaultValue;
                }
                if (i > 0){
                    func(name, element.text(), i);
                }
            }
        }
    } else {
        print(root.tagName() + " is invalid");
    }
}


ParameterObject::ParameterObject(){
};

MyApp::MyApp(const QString & directory, const QString & service_file){
    for (QFileInfo info : getFileList(directory)){
        if (info.fileName().endsWith(".service") && info.isFile()){
            auto object = std::make_shared<ServiceObject>(info.absoluteFilePath());
            this->services[object->name] = object;
        }
    }
    this->service_file = service_file;
}

QString MyApp::getServiceDefaultParam(const QString & name){
    if (this->services.contains(name)){
        auto ptr = this->services[name];
        if (!ptr->parameters.isEmpty()){
            return ptr->parameters.begin().key();
        }
    }
    return "";
}

QString MyApp::getParamDefaultValue(const QString &name, const QString &param){
    if (this->services.contains(name)){
        auto ptr = this->services[name];
        if (!ptr->parameters.isEmpty()){
            return ptr->parameters[param]->defaultValue;
        }
    }
    return "";
};

QStringList MyApp::getServices(){
    return this->services.keys();
};

QStringList MyApp::getParamValues(const QString &name, const QString &param){
    if (this->services.contains(name)){
        auto ptr = this->services[name];
        if (!ptr->parameters.isEmpty()){
            return ptr->parameters[param]->allowedValues;
        }
    }
    return QStringList();
};

QStringList MyApp::getServiceParams(const QString &name){
    if (this->services.contains(name)){
        auto ptr = this->services[name];
        if (!ptr->parameters.isEmpty()){
            return ptr->parameters.keys();
        }
    }
    return QStringList();
};

std::shared_ptr<ParameterObject> ServiceObject::getParameterObject(const QString & name){
    if (!this->parameters.contains(name)){
        auto ret = std::make_shared<ParameterObject>();
        this->parameters[name] = ret;
        ret->name = name;
        return ret;
    }
    return this->parameters[name];
};



ServiceObject::ServiceObject(const QString & service_file){
    DescriptionParse(service_file, [this](QString name, QString mode, int id){
        QString str;
        switch (id){
            case ServiceTag::ServiceSummary:
                this->summary = mode;
                this->name = name;
                break;
            case ServiceTag::ServiceDescription:
                this->description = mode;
                this->name = name;
                break;
            case ServiceTag::ParameterDescription:
                {
                    auto param = getParameterObject(name);
                    param->description = mode;
                }
                break;
            case ServiceTag::DefaultValue:
                {
                    auto param = getParameterObject(name);
                    param->defaultValue = mode;
                }
                break;
            case ServiceTag::AllowedValue:
                {
                    auto param = getParameterObject(name);
                    param->allowedValues.append(mode);
                }
                break;
            default:
                break;
        }
    });
}

QVariantMap ParameterMap(const QString &value, const QStringList & list, const QString & defaultValue){
    QVariantMap param;
    param["description"] = value;
    if (list.size() > 0){
        QVariantList l;
        for (QString str : list){
            l << str;
        }
        param["values"] = l;
    }
    if (!defaultValue.isEmpty()){
        param["default"] = defaultValue;
    }
    return param;
}

QVariantMap ParameterMap(ParameterObject * object){
    return ParameterMap(object->description, object->allowedValues, object->defaultValue);
}

QVariantMap ParameterMap(std::shared_ptr<ParameterObject> object){
    return ParameterMap(object.get());
}

void ServiceMapFinalize(
    QVariantMap  & map1,
    QMap<QString, QString>  & paramDesc,
    QMap<QString, QString>  & defaults,
    QMap<QString, QStringList>  & paramAllowedValues){

    QVariantMap params;
    for (auto [key, value] : paramDesc.asKeyValueRange()){
        QStringList list;
        QString def;
        if (paramAllowedValues.contains(key)){
            list = paramAllowedValues[key];
        }
        if (defaults.contains(key)){
            def = defaults[key];
        }
        params[key] = ParameterMap(value, list, def);
    }
    if (!params.isEmpty()){
        map1["parameters"] = params;
    }
}

QVariantMap ServiceMap(ServiceObject * object){
    QVariantMap map1;
    QMap<QString, QString> paramDesc;
    QMap<QString, QString> defaults;
    QMap<QString, QStringList> paramAllowedValues;
    // info service

    map1["summary"] = object->summary;
    map1["name"] = object->name;
    map1["description"] = object->description;

    for (auto [key, value] : object->parameters.asKeyValueRange()){
        paramDesc[key] = value->description;
        auto & defaultValue = value->defaultValue;
        auto & allowedValues = value->allowedValues;
        if (!defaultValue.isEmpty()){
            defaults[key] = defaultValue;
        }
        if (!allowedValues.isEmpty()){
            paramAllowedValues[key] = allowedValues;
        }
    }
    ServiceMapFinalize(map1, paramDesc, defaults, paramAllowedValues);
    return map1;
}

QVariantMap ServiceMap(std::shared_ptr<ServiceObject> object){
    return ServiceMap(object.get());
}

QVariantMap ServiceMap(const QString & service_file){
    QVariantMap map1;
    QMap<QString, QString> paramDesc;
    QMap<QString, QString> defaults;
    QMap<QString, QStringList> paramAllowedValues;
    // info service
    DescriptionParse(service_file, [&defaults, &map1, &paramDesc, &paramAllowedValues](QString name, QString mode, int id){
        QString str;
        switch (id){
            case ServiceTag::ServiceSummary:
                map1["summary"] = mode;
                map1["name"] = name;
                break;
            case ServiceTag::ServiceDescription:
                map1["description"] = mode;
                map1["name"] = name;
                break;
            case ServiceTag::ParameterDescription:
                paramDesc[name] = mode;
                break;
            case ServiceTag::DefaultValue:
                defaults[name] = mode;
                break;
            case ServiceTag::AllowedValue:
            {
                if (!paramAllowedValues.contains(name)){
                    paramAllowedValues[name] = QStringList();
                }
                QStringList & values = paramAllowedValues[name];
                values.append(mode);
            }
            default:
                break;
        }
    });
    ServiceMapFinalize(map1, paramDesc, defaults, paramAllowedValues);
    return map1;
}

QString MyApp::showService(const QString & serviceName){
    QString text = "";
    if (this->services.contains(serviceName)){
        text = dictToYaml(ServiceMap(this->services[serviceName]), {"parameters", "name"});
    }
    return text;
}

bool MyApp::save(const QString & content){
    QFile file(service_file);
    if (file.open(QFile::WriteOnly)){
        auto array = content.toUtf8();
        return file.write(array) == array.size();
    } else {
        return false;
    }
}

QString MyApp::showParam(const QString & serviceName, const QString & param){
    QString text = "";
    if (this->services.contains(serviceName)){
        auto obj = this->services[serviceName];
        if (obj->parameters.contains(param)){
            text = dictToYaml(ParameterMap(this->services[serviceName]->parameters[param]), {"name"});
        }
    }
    return text;
}

QString slurp(const QString &path)
{
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly))
        return "";

    return QString::fromUtf8(f.readAll()).trimmed();
}

void XmlParse(const QString & filepath, std::function<void(const QString&, const QString&, int)> func, bool skip_params = false){
    QDomDocument doc;
    QDomElement root;

    QFileInfo fileinfo(filepath);
    {
        QDir filedir = fileinfo.absoluteDir();
        filedir = filedir.absoluteFilePath(".osc");
        QFileInfo newinfo(filedir.absolutePath());
        if (newinfo.isDir()){
            QDir newdir(newinfo.absoluteFilePath());
            putenv("OBS_SERVICE_PACKAGE", slurp(newdir.absoluteFilePath("_package")).toUtf8());
            putenv("OBS_SERVICE_APIURL", slurp(newdir.absoluteFilePath("_apiurl")).toUtf8());
            putenv("OBS_SERVICE_PROJECT", slurp(newdir.absoluteFilePath("_project")).toUtf8());
        }
    }

    QFile file(fileinfo.absoluteFilePath());

    int i = 0;
    QDomNodeList items;
    if (!file.open(QIODevice::ReadOnly)) {
        print("cannot open file");
        goto last_label;
    }
    if (!doc.setContent(&file)) {
        print("invalid XML");
        file.close();
        goto last_label;
    }
    file.close();

    root = doc.documentElement();
    {
        QString tag_name = root.tagName();
        print("Root: " + tag_name);
        if (tag_name != "services"){
            goto last_label;
        }
    }
    items = root.elementsByTagName("service");
    for (auto serv : items) {
        QDomElement e = serv.toElement();
        QString name, mode;
        name = e.attribute("name");
        if (name.isEmpty() || name == ""){
            continue;
        }
        print(
            "name = " + name
        );
        print(
            "mode = " + (mode = e.attribute("mode"))
        );
        i ++;
        func(name, mode, i);
        if (!skip_params){
        for (auto p : e.elementsByTagName("param")){
            QDomElement param = p.toElement();
            QString name, text;
            name = param.attribute("name");
            if (name.isEmpty() || name == ""){
                continue;
            }
            print(
                "param name = " + name
            );
            print(
                "param text = " + (text = param.text())
            );
            func(name, text, i);
        } }
    }
    last_label:
    func("", "", -1);
}


QVariantList knownServices(const QString & filepath){
    int cr = 0;
    QVariantList ret;
    QVariantList serv;
    QVariantList params;
    XmlParse(filepath, [&cr, &serv, &ret, &params](
            const QString & name, const QString & mode, int type){
        if (type != cr){
            if (cr > 0){
                serv.append(QVariant(params));
                ret.append(QVariant(serv));
                params = QVariantList();
                serv = QVariantList();
            }
            if (type > 0){
                cr = type;
                serv.append(name);
                serv.append(mode);
            }
        } else {
            QVariantList plist;
            plist.append(name);
            plist.append(mode);
            params.append(QVariant(plist));
        }
    });
    return ret;
}

bool createHardLink(const fs::path& source, const fs::path& link) {
    try {
        // Attempt to create a hard link
        fs::create_hard_link(source, link);
        return true;
    } catch (const std::filesystem::filesystem_error& e) {
        return false;
    }
}

bool createSymlink(const fs::path& source, const fs::path& symlink) {
    try {
        // Attempt to create a symbolic link
        fs::create_symlink(source, symlink);
        return true;
    } catch (const std::filesystem::filesystem_error& e) {
        return false;
    }
}

bool createHardLinkWithOverwrite(const QString &source, const QString &destination) {
    // If the destination file exists, remove it first
    if (QFile::exists(destination)) {
        if (QFile::remove(destination)) {
        } else {
            return false;
        }
    }

    string src = source.toStdString();
    string dest = destination.toStdString();
    if (createHardLink(src, dest)){
        return true;
    } else {
        return createSymlink(src, dest);
    }
}

struct ServiceJob{
    QList<Service> manualList;
    QList<Service> serverList;
    QList<Service> buildList;

    int Run(const QString & workdir){
        QDir temporarydir (workdir + "/.osc.temp");
        QDir olddir (temporarydir.absoluteFilePath("_old_dir"));
        QDir oldtempdir(olddir.absoluteFilePath(generateRandomString(16)));
        oldtempdir.mkpath(".");

        QFileInfoList entries = temporarydir.entryInfoList(
            QDir::NoDotAndDotDot | QDir::AllEntries
        );

        for (const QFileInfo &info : entries) {
            QString filename = info.fileName();
            if (filename == "_old_dir"){
                continue;
            }
            QString srcPath = info.absoluteFilePath();
            QString dstPath = oldtempdir.filePath(filename);
            // rename() moves files and directories
            if (!QFile::rename(srcPath, dstPath)) {

            }
        }

        QDir servicedir (temporarydir.absoluteFilePath("_service_dir"));
        QDir builddir (temporarydir.absoluteFilePath("_output_dir"));

        servicedir.mkpath(".");
        builddir.mkpath(".");

        bool local = manualList.count() > 0;
        bool server = serverList.count() > 0;
        bool build = buildList.count() > 0;

        repeat:
        for (auto info:  getFileList(workdir)){
            QString absolute_info = info.absoluteFilePath();
            createHardLinkWithOverwrite(absolute_info, servicedir.absoluteFilePath(info.fileName()));
            createHardLinkWithOverwrite(absolute_info, builddir.absoluteFilePath(info.fileName()));
        }

        int lastError = 0;

        auto cpio_extract = [](const QString & builddir) {
            for (auto info: getFileList(builddir)){
                if (info.isFile() && info.fileName().endsWith(".obscpio", Qt::CaseInsensitive)){
                    qDebug() << "extract: >> " << info.fileName();
                    extractCpioFromStream(info.absoluteFilePath());
                }
            }
        };

        auto lambda = [&lastError, temporarydir, cpio_extract](const QString & dir, Service & serv){
            QDir servicedir(dir);
            QDir outdir(QDir(dir).absoluteFilePath("tmp" + generateRandomString(8) + "." + serv.name + ".service"));
            outdir.mkpath(".");
            int i = serv.Run(dir, outdir);
            if (i != 0) lastError = i;
            for (auto info:  getFileList(outdir)){
                QString fileName = info.fileName();
                QString absolute_info = info.absoluteFilePath();
                createHardLinkWithOverwrite(absolute_info, servicedir.absoluteFilePath(fileName));
            }
            outdir.removeRecursively();
        };

        if (local){
            for (Service & serv: manualList){
                lambda(workdir, serv);
            }
            local = false;
            goto repeat;
        }

        if (server){
            for (Service & serv: serverList){
                QDir outdir(temporarydir.absoluteFilePath("_temp_dir_"+ serv.name + "_" +generateRandomString(16)));
                outdir.mkpath(".");
                int i = serv.Run(servicedir, outdir);
                if (i != 0) lastError = i;

                for (auto info:  getFileList(outdir)){
                    QString fileNameSmp = info.fileName();
                    QString token = "";
                    if (fileNameSmp.startsWith("_service:")){
                        QRegularExpression re(R"(^_service:([A-Za-z0-9_-])+:(.*))");
                        auto match = re.match(fileNameSmp);
                        if (match.hasMatch()) {
                            token = match.captured(1);
                            fileNameSmp = match.captured(2);
                            int ind = fileNameSmp.lastIndexOf(':');
                            if (ind > 0){
                                token += ":" + fileNameSmp.sliced(0, ind);
                                fileNameSmp = fileNameSmp.sliced(ind + 1);
                            }
                            token += ':';
                        }
                    }
                    QString fileName = "_service:" + serv.name + ":" + token + fileNameSmp;
                    QString absolute_info = info.absoluteFilePath();
                    createHardLinkWithOverwrite(absolute_info, servicedir.absoluteFilePath(fileName));
                    createHardLinkWithOverwrite(absolute_info, builddir.absoluteFilePath(fileNameSmp));
                }
            }
        }

        QString builddir_str = builddir.absolutePath();
        cpio_extract(builddir_str);

        if (build){
            for (Service & serv: buildList){
                lambda(builddir_str, serv);
            }
        }
        return lastError;
    }
};


bool isServiceAllowed(const QString & mode, bool local, bool server, bool build){
    return
    (mode == "" && server ) ||
    (mode == "trylocal" && (server || local) ) ||
    (mode == "localonly" && local ) ||
    (mode == "serveronly" && server ) ||
    (mode == "buildtime" && build ) ||
    (mode == "manual" && local );
}

void RunService(
        ServiceJob & job,
        const QString & serviceDir,
        const QString & name,
        const QString & mode,
        QList<Parameter> par,
        bool local,
        bool server,
        bool build
){
    QString path = QDir::cleanPath(serviceDir + QDir::separator() + name);
    if ( local && (
        mode == "serveronly" ||
        mode == "" ||
        mode == "trylocal")
    ){
        job.serverList << Service(path, par, name);
    } else if ( server && (
        mode == "trylocal" ||
        mode == "localonly" ||
        mode == "manual")
    ) {
        job.manualList << Service(path, par, name);
    } else if ( build && (
        mode == "buildtime")
    ) {
        job.buildList << Service(path, par, name);
    }
}


typedef int (*obs_edit_ref)(int argc, char ** argv, QObject * app_instance, const QVariantList & list);

obs_edit_ref obs_edit;

int main(int argc, char ** argv){
    putenv("OSC_VERSION", "1.27.0");

    QString service_file = "_service";
    QString repolist_file = "_repolist";
    QString info_service = "";
    
 //   app.setApplicationName("obs_tools");
 //   app.setApplicationVersion("1.0");

    // Create parser
    QCommandLineParser parser;
    parser.setApplicationDescription("obs_tools cli app");
    parser.addHelpOption();
    parser.addVersionOption();

    // Add options
    QCommandLineOption workdirOption(QStringList() << "workdir",
                                  "Working directory", "dirname");
    parser.addOption(workdirOption);

    QCommandLineOption verboseOption(QStringList() << "verbose",
                                  "Enable verbose output");
    parser.addOption(verboseOption);

    QCommandLineOption serviceOption(QStringList() << "service",
                                  "Service file", "service");
    parser.addOption(serviceOption);

    QCommandLineOption repolistOption(QStringList() << "repolist",
                                  "Repolist file", "repolist");
    parser.addOption(repolistOption);

    QCommandLineOption pkgsOption(QStringList() << "listpkgs",
                                  "List packages");
    parser.addOption(pkgsOption);

    QCommandLineOption reposOption(QStringList() << "listrepos",
                                  "List Repos");
    parser.addOption(reposOption);

    QCommandLineOption localOption(QStringList() << "local",
                                  "local only");
    parser.addOption(localOption);

    QCommandLineOption buildOption(QStringList() << "build",
                                  "buildtime only");
    parser.addOption(buildOption);

    QCommandLineOption serverOption(QStringList() << "server",
                                  "server only");
    parser.addOption(serverOption);

    QCommandLineOption listOption(QStringList() << "list",
                                  "List services");
    parser.addOption(listOption);

    QCommandLineOption editOption(QStringList() << "edit",
                                  "Edit service");
    parser.addOption(editOption);

    QCommandLineOption infoOption(QStringList() << "info",
                                  "Get information about service", "name");
    parser.addOption(infoOption);
    // Process the actual command line arguments
    QStringList list;
    for (int i = 0; i <  argc; i ++){
        list << argv[i];
    }
    parser.process(list);

    bool local = parser.isSet(localOption);
    bool build = parser.isSet(buildOption);
    bool server = parser.isSet(serverOption);
    bool pkglist = parser.isSet(pkgsOption);
    bool servicelist = parser.isSet(listOption);
    bool reposlist = parser.isSet(reposOption);
    bool editserv = parser.isSet(editOption);

    if (parser.isSet(serviceOption)) {
        service_file = parser.value(serviceOption);
    }
    if (parser.isSet(repolistOption)) {
        repolist_file = parser.value(repolistOption);
    }
    if (parser.isSet(infoOption)) {
        info_service = parser.value(infoOption);
    }
    if (parser.isSet(verboseOption)) {
        verbose_mode = true;
        print("verbose mode");
    }
    if (!info_service.isEmpty()){
        info_service = QString(obs_path) + QDir::separator() + info_service + ".service";
        print(info_service);
        std::cout << dictToYaml(ServiceMap(info_service)).toStdString() << std::endl;
        return 0;
    }

    QString workdir;
    if (parser.isSet(workdirOption)) {
        workdir = parser.value(workdirOption);
        QFileInfo info(workdir);
        if (info.exists()){
            if (info.isDir()){
                workdir = info.absoluteFilePath();
                QDir::setCurrent(workdir);
                print("working directory: " + workdir);
                goto skip1;
            }
        }
        print("directory does not exists: " + workdir);
        return 1;
    }
    workdir = QDir::currentPath();
    skip1:

    if (editserv){
        auto app_instance = new MyApp(obs_path, service_file);
        QVariantList list = knownServices(service_file);

        void *handle = dlopen("libobs_edit.so", RTLD_LAZY);
        if (!handle) {
            std::cerr << "dlopen failed: " << dlerror() << std::endl;
            return 1;
        }

        // Clear any existing errors
        dlerror();

        // Load the symbol
        obs_edit = (obs_edit_ref)dlsym(handle, "obs_edit");
        const char *error = dlerror();
        if (error) {
            std::cerr << "dlsym failed: " << error << std::endl;
            dlclose(handle);
            return 1;
        }

        // Call the function
        int ret = obs_edit(argc, argv, app_instance, list);

        // Close the library
        dlclose(handle);

        return ret;
    }
    if (QFile::exists(service_file)){
        print("_service exists");
        if (reposlist){
            for (QString str : getRepos(repolist_file)){
                std::cout << str.toStdString() << std::endl;
            }
        } else if (pkglist){
            for (QString str : getPackages(service_file, repolist_file)){
                std::cout << str.toStdString() << std::endl;
            }
        } else if (servicelist){
            XmlParse(service_file, [local, build, server](QString name, QString mode, int par){
                if (
                    isServiceAllowed(mode, local, build, server)
                ){
                    std::cout << name.toStdString() << std::endl;
                }
            }, true);
        } else {
            ServiceJob service;
            QStringList absent;
            XmlParse(service_file, [local, build, server, &absent](QString name, QString mode, int par){
                if (par < 0) return; 
                if (
                    isServiceAllowed(mode, local, build, server)
                ){
                    QFileInfo info(QString(obs_path) + QDir::separator() + name);
                    if (!info.isFile()){
                        absent << name;
                    }
                }
            }, true);
            if (absent.isEmpty()){
                int create = 0;
                QString name, mode;
                QList<Parameter> par;
                XmlParse(service_file, [&name, &mode, &par, &service, local, build, server, &create](QString a1, QString a2, int par1){
                    if (par1 != create){
                        if (create != 0){
                            RunService(service, obs_path, name, mode, par, local, server, build);
                        }
                        name = a1;
                        mode = a2;
                        create = par1;
                        par.clear();
                    } else {
                        par << Parameter(a1, a2);
                    }
                }, false);
            } else {
                for (QString str : absent){
                    std::cout << "Service " << str.toStdString() << " not installed" << std::endl;
                }
            }
            service.Run(workdir);
        }
    } else {
        print("_service does not exsits");
        return 2;
    }
}
