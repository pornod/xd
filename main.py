from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient
from JDatabase import JsonDatabase
import zipfile
import os
import infos
import shortener
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import S5Crypto
import random
####################################################
saveconfig = "✅Configuración Guardada"
proxy_list = []
###################################################


#ef nameRamdom():
   # populaton = 'abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
   # name = "".join(random.sample(populaton,10))
   # return name
def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        filename = filename.replace(" ", "_")
        bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚊𝚗𝚍𝚘 𝚙𝚊𝚛𝚊 𝚜𝚞𝚋𝚒𝚛☁...')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        if cloudtype == 'moodle':
            client = MoodleClient(user_info['moodle_user'],
                                  user_info['moodle_password'],
                                  user_info['moodle_host'],
                                  user_info['moodle_repo_id'],
                                  proxy=proxy)
            loged = client.login()
            itererr = 0
            if loged:
                if user_info['uploadtype'] == 'evidence':
                    evidences = client.getEvidences()
                    evidname = str(filename).split('.')[0]
                    for evid in evidences:
                        if evid['name'] == evidname:
                            evidence = evid
                            break
                    if evidence is None:
                        evidence = client.createEvidence(evidname)

                originalfile = ''
                if len(files)>1:
                    originalfile = filename
                draftlist = []
                for f in files:
                    f_size = get_file_size(f)
                    resp = None
                    iter = 0
                    tokenize = False
                    if user_info['tokenize']!=0:
                       tokenize = True
                    while resp is None:
                          if user_info['uploadtype'] == 'evidence':
                             fileid,resp = client.upload_file(f,evidence,fileid,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'draft':
                             fileid,resp = client.upload_file_draft(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'blog':
                             fileid,resp = client.upload_file_blog(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'calendar':
                             fileid,resp = client.upload_file_calendar(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'calendarevea':
                             fileid,resp = client.upload_file_calendarevea(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          iter += 1
                          if iter>=10:
                              break
                    os.unlink(f)
                if user_info['uploadtype'] == 'evidence':
                    try:
                        client.saveEvidence(evidence)
                    except:pass
                return draftlist
            else:
                bot.editMessageText(message,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚎𝚗 𝚕𝚊 𝚗𝚞𝚋𝚎⚠️')
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            bot.editMessageText(message,'🚀Subiendo ☁ Espere por favor...😄')
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)
               return filesdata
        return None
    except Exception as ex:
        bot.editMessageText(message,'Error\n' + str(ex))
        return None

def processFile(update,bot,message,file,thread=None,jdb=None):
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        #zipname = str(name).split('.')[0] + createID()
        zipname = str(file).split('.')[0]
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        client = processUploadFiles(file,file_size,multi_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(name)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(file,file_size,[file],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚊𝚗𝚍𝚘 𝚊𝚛𝚌𝚑𝚒𝚟𝚘📄...')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(name).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' or getUser['uploadtype'] == 'blog' or getUser['uploadtype']=='calendar' or getUser['uploadtype']=='calendarevea':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        bot.deleteMessage(message.chat.id,message.message_id)
        #finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex)
        finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex, update.message.sender.username)
        filesInfo = infos.createFileMsg(file,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        bot.sendMessage(-752493950,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
    else:
        bot.editMessageText(message,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚎𝚗 𝚕𝚊 𝚗𝚞𝚋𝚎⚠️')

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    file_name = file_name.replace(" ", "_")
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)
        # else:
        #     megadl(update,bot,message,url,file_name,thread,jdb=jdb)

# def megadl(update,bot,message,megaurl,file_name='',thread=None,jdb=None):
#     megadl = megacli.mega.Mega({'verbose': True})
#     megadl.login()
#     try:
#         info = megadl.get_public_url_info(megaurl)
#         file_name = info['name']
#         megadl.download_url(megaurl,dest_path=None,dest_filename=file_name,progressfunc=downloadFile,args=(bot,message,thread))
#         if not megadl.stoping:
#             processFile(update,bot,message,file_name,thread=thread)
#     except:
#         files = megaf.get_files_from_folder(megaurl)
#         for f in files:
#             file_name = f['name']
#             megadl._download_file(f['handle'],f['key'],dest_path=None,dest_filename=file_name,is_public=False,progressfunc=downloadFile,args=(bot,message,thread),f_data=f['data'])
#             if not megadl.stoping:
#                 processFile(update,bot,message,file_name,thread=thread)
#         pass
#     pass

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                bot.sendFile(-752493950,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        tl_admin_user = os.environ.get('nautaii')

        #set in debug
        tl_admin_user = os.environ.get('nautaii')

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "Usted no tiene acceso.\nPor favor Contacta con mi Programador @"+"Luis_Daniel_Diaz"+"/n"
            intento_msg = "💢El usuario @"+username+ " ha intentando usar el bot sin permiso💢"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(1759969205,intento_msg)
            return


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '✅El usuario @'+user+' ah sido agregado al bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️Error en el comando /add usuario')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = '❇️Ahora @'+user+' es admin del bot también.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️Error en el comando /admin usuario⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return

        if '/prueba' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user_evea_preview(user)
                    jdb.save()
                    msg = '✅El usuario @'+user+' ahora está en modo prueba.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️Error en el comando /preview usuario⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return 
        if '/ban' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'⚠️No puede banearse a si mismo⚠️')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '🚫El usuario @'+user+' ah sido baneado del bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /ban usuario⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/obtenerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                sms1 = bot.sendMessage(update.message.chat.id,'Enviando la databse del bot...')
                sms2 = bot.sendMessage(update.message.chat.id,'Base de datos👇🏻:')
                
                bot.editMessageText(sms1,sms2)
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️')
            return
        if '/leerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'⚠️')
            return
        if '/useradm' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                message = bot.sendMessage(update.message.chat.id,'🦾')
                message = bot.sendMessage(update.message.chat.id,'🦾Es administrador del bot así que tiene control total sobre el mismo✅')
            else:
                message = bot.sendMessage(update.message.chat.id,'🙁')
                message = bot.sendMessage(update.message.chat.id,'🙁Usted es solo usuario, por ahora tiene control parcialmente sobre el bot❎')
            return
        # end

        # comandos de usuario

        if '/xdlink' in msgText:

            try: 
                urls = str(msgText).split(' ')[1]
                channelid = getUser['channelid']
                xdlinkdd = xdlink.parse(urls, username)
                msg = f'🔗Aquí está su link encriptado en xdlink:🔗 `{xdlinkdd}`'
                msgP = f'🔗Aquí está su link encriptado en xdlink protegido:🔗 `{xdlinkdd}`'
                if channelid == 0:
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
                else: 
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msgP)
            except:
                msg = f'📌El comando debe ir acompañado de un link moodle...'
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/xdon' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 1
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
            
        if '/xdoff' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return

        if '/channelid' in msgText:
            channelId = str(msgText).split(' ')[1]
            getUser = user_info
            try:
                if getUser:
                    getUser['channelid'] = str(msgText).split(' ')[1]
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'╭───ⓘ☣️El comando debe ir acompañado de un id de canal...\n╰⊸\n💡Ejemplo: -100XXXXXXXXXX.')
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/delchannel' in msgText:
            getUser = user_info
            if getUser:
                getUser['channelid'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
        if '/login' in msgText:
             import requests
             getUser = user_info
             if getUser:
                user = getUser['moodle_user']
                passw = getUser['moodle_password']
                host = getUser['moodle_host']
                proxy = getUser['proxy']
                url = host
                r = requests.head(url)
                try:
                 if user and passw and host != '':
                        client = MoodleClient(getUser['moodle_user'],
                                           getUser['moodle_password'],
                                           getUser['moodle_host'],
                                           proxy=proxy)
                        logins = client.login()
                        if logins:
                                bot.editMessageText(message,"✅Conexion lista :D...")  
                                return
                        else: 
                            bot.editMessageText(message,"☣️Error al conectar...")
                            message273= bot.sendMessage(update.message.chat.id,"🔎Escaneando pagina...")
                            if r.status_code == 200 or r.status_code == 303:
                                bot.editMessageText(message273,f"🧾Estado de la pagina: {r}\n☣️Revise que su cuenta no ah sido baneada...")
                                return
                            else: bot.editMessageText(message273,f"🚷Pagina caida, estado: {r}")    
                            return
                except Exception as ex:
                            bot.editMessageText(message273,"☣️Tipo de error: "+str(ex))    
                else: bot.editMessageText(message,"☣️No ha puesto sus credenciales")    
                return
        if '/watch' in msgText:
            import requests
            url = user_info['moodle_host']
            msg2134=bot.editMessageText(message,f"Escaneando url guardado en info")
            try:
             r = requests.head(url)
             if r.status_code == 200 or r.status_code == 303:
                bot.editMessageText(msg2134,f"Pagina: {url} activa")
             else: bot.editMessageText(msg2134,f"Pagina: {url} caida")
            except Exception as ex:
                bot.editMessageText(message,"Error al escanear"+str(ex))
        if '/shorturl' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['urlshort']==0:
                            jdb.items[user]['urlshort'] = 1
                            continue
                        if jdb.items[user]['urlshort']==1:
                            jdb.items[user]['urlshort'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'✅ShortUrl Cambiado✅')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id, statInfo,)
                except:
                    bot.sendMessage(update.message.chat.id,'Error en el Shorturl...')
            return

        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🙃')
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return
        if '/about' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🤩')
            información = open('información.txt','r')
            bot.sendMessage(update.message.chat.id,información.read())
            información.close()
            return
        if '/commands' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🙂Para añadir estos comandos al menú de acceso rápido debe enviarle el comando /setcommands a @BotFather y luego seleccionar su bot, luego solo queda reenviarle el mensaje con los siguientes comandos y bualah😁.')
            comandos = open('comandos.txt','r')
            bot.sendMessage(update.message.chat.id,comandos.read())
            información.close()
            return
        if '/info' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '🗜️Perfecto ahora los zips serán de '+ sizeof_fmt(size*1024*1024)+' las partes📚'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /zips tamaño de zips⚠️')    
                return
        #if '/gen' in msgText:
            #pass444
        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /acc usuario,contraseña⚠️')
            return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /host url de la nube⚠️')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /repo ID de la moodle⚠️')
            return
        #if '/encrypt_on' in msgText:
            #try:
                #getUser = user_info
                #if getUser:
                    #getUser['tokenize'] = 1
                    #jdb.save_data_user(username,getUser)
                    #jdb.save()
                    #statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    #bot.sendMessage(update.message.chat.id,'🔮Encriptar enlaces de descarga.')
            #except:
                #bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /encrypt_on estado de Encriptar⚠️')
            #return
        #if '/encrypt_off' in msgText:
            #try:
                #getUser = user_info
                #if getUser:
                    #getUser['tokenize'] = 0
                    #jdb.save_data_user(username,getUser)
                    #jdb.save()
                    #statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    #bot.sendMessage(update.message.chat.id,'🔮No Encriptar enlaces de descarga.')
            #except:
                #bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /encript_off estado de Encriptar⚠️')
            #return
        if '/cloud' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['cloudtype'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /cloud (moodle o cloud⚠️')
            return
        if '/uptype' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando up tipo de subida (evidence,draft,blog,calendar)⚠️')
            return

        if '/search_proxy' in msgText:
            msg_start = 'Buscando proxy, esto puede tardar de una a dos horas...'
            bot.sendMessage(update.message.chat.id,msg_start)
            print("Buscando proxy...")
            for port in range(3029,3032):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                result = sock.connect_ex(('152.206.139.117:',port))  

                if result == 0: 
                    print ("Puerto abierto!")
                    print (f"Puerto: {port}")  
                    proxy = f'152.206.139.117:{port}'
                    proxy_new = S5Crypto.encrypt(f'{proxy}')
                    msg = 'Su nuevo proxy es:\n\nsocks5://' + proxy_new
                    bot.sendMessage(update.message.chat.id,msg)
                    break
                else: 
                    print ("Error...Buscando...")
                    print (f"Buscando en el puerto: {port}")
                    sock.close()
            
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🧬Perfecto, proxy equipado exitosamente.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🧬Error al equipar proxy.')
            return
        if '/crypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🧬Proxy encriptado:\n{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🧬 Proxy desencriptado:\n{proxy_de}')
            return
        if '/off_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🧬Bien, proxy desequipado exitosamente.\n'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🧬Error al desequipar proxy.')
            return
        if '/view_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    proxy = getUser['proxy']
                    message = bot.sendMessage(update.message.chat.id,'🧬El proxy usado actualmente es:👇🏻')
                    bot.sendMessage(update.message.chat.id,proxy)
            except:
                message = bot.sendMessage(update.message.chat.id,'🧬El proxy usado actualmente es:👇🏻')
                bot.sendMessage(update.message.chat.id,proxy)
            return
        if '/dir' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['dir'] = repoid + '/'
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /dir carpeta destino⚠️')
            return
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'🚫𝚃𝙰𝚁𝙴𝙰 𝙲𝙰𝙽𝙲𝙴𝙻𝙰𝙳𝙰🚫')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'⏳𝙰𝙽𝙰𝙻𝙸𝚉𝙰𝙽𝙳𝙾...⌛')

        thread.store('msg',message)

        if '/start' in msgText:
            #bot.editMessageText(message,'🦾')
            start_msg = '╭───ⓘ🌟𝔹𝕆𝕋 𝕀ℕ𝕀ℂ𝕀𝔸𝔻𝕆🌟─〄\n│\n'
            start_msg+= '├⊸🤖Hola @' + str(username)+' !!!!\n│\n'
            start_msg+= '├─⊰᯽⊱┈──╌❊ - ❊╌──┈⊰᯽⊱─⊸\n│\n'
            start_msg+= '├⊸☺️! Bienvenid@ al bot de descargas gratis SuperDownload en su versión 1.5🌟!\n'
            start_msg+= '├⊸🙂Si necesita ayuda o información utilice:\n│\n'
            start_msg+= '├⊸/help\n'
            start_msg+= '├⊸/about\n'
            start_msg+= '├⊸/config\n│\n'
            start_msg+= '├⊸🙂Si usted desea añadir la barra de comandos al menú de acceso rápido de su bot envíe /commands.\n│\n'
            start_msg+= '├⊸😁𝚀𝚞𝚎 𝚍𝚒𝚜𝚏𝚛𝚞𝚝𝚎 𝚐𝚛𝚊𝚗𝚍𝚎𝚖𝚎𝚗𝚝𝚎 𝚜𝚞 𝚎𝚜𝚝𝚊𝚍í𝚊😁.\n│\n'
            start_msg+= '╰───ⓘSuperDownload 🌟─〄\n'
            bot.editMessageText(message,start_msg)
            message = bot.sendMessage(update.message.chat.id,'🦾')
        elif '/files' == msgText and user_info['cloudtype']=='moodle':
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:

                List = client.getEvidences()
                List1=List[:45]
                total=len(List)
                List2=List[46:]
                info1 = f'<b>Archivos: {str(total)}</b>\n\n'
                info = f'<b>Archivos: {str(total)}</b>\n\n'
                
                i = 0
                for item in List1:
                    info += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                    #info += '<b>'+item['name']+':</b>\n'
                    for file in item['files']:                  
                        info += '<a href="'+file['directurl']+'">\t'+file['name']+'</a>\n'
                    info+='\n'
                    i+=1
                    bot.editMessageText(message, f'{info}',parse_mode="html")
                
                if len(List2)>0:
                    bot.sendMessage(update.message.chat.id,'⏳Conectando con Lista número 2...')
                    for item in List2:
                        
                        info1 += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                        #info1 += '<b>'+item['name']+':</b>\n'
                        for file in item['files']:                  
                            info1 += '<a href="'+file['url']+'">\t'+file['name']+'</a>\n'
                        info1+='\n'
                        i+=1
                        bot.editMessageText(message, f'{info1}',parse_mode="html")
        elif '/txt_' in msgText and user_info['cloudtype']=='moodle':
             findex = str(msgText).split('_')[1]
             findex = int(findex)
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 evidences = client.getEvidences()
                 evindex = evidences[findex]
                 txtname = evindex['name']+'.txt'
                 sendTxt(txtname,evindex['files'],update,bot)
                 client.logout()
                 bot.editMessageText(message,'𝚃𝚇𝚃 𝙰𝚚𝚞𝚒👇')
             else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
             pass
        elif '/delete' in msgText:
           try: 
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "✅Archivo eliminado con exito.•°🗑️")
            else: bot.sendMessage(update.message.chat.i, "😰No fue posible loguearse.")            
           except: bot.sendMessage(update.message.chat.id, "❌No fue posible eliminar el archivo.")
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'🤖Obteniendo Token, por favor espere🙂...')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'🤖Su Token es: '+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'⚠️La Moodle '+client.path+' no tiene Token⚠️')
            except Exception as ex:
                bot.editMessageText(message2,'⚠️La moodle '+client.path+' no tiene Token o revise la cuenta⚠️')
        elif '/config' in msgText:
            msg_nub = "╭───ⓘ💡LISTA DE NUBES PRECONFIGURADAS:\n"
            msg_nub += "├⊸☁️ UCLV ☛ /uclv\n"
            msg_nub += "├⊸☁️ Aulacened ☛ /aulacened\n"
            msg_nub += "├⊸☁️ Cursos ☛ /cursos\n"
            msg_nub += "├⊸☁️ Evea ☛ /evea\n"
            msg_nub += "├⊸☁️ Eduvirtual ☛ /eduvirtual\n"
            msg_nub += "├⊸☁️ Eva ☛ /eva\n"
            msg_nub += "╰⊸☁️ Art.sld ☛ /artem\n"   
            bot.editMessageText(message,msg_nub)

        elif '/delconf' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "--"
            getUser['uploadtype'] =  "--"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 100
            getUser['proxy'] = ""
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"🗑Configuración Eliminada🗑")

        elif '/delete_prox' in msgText: 
            getUser = user_info
            getUser['proxy'] = ""
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"🗑Proxy Eliminado🗑")
        ###############################################################
        
        elif '/aulacened' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulacened.uci.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 248
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aulacened cargada...")
           
        elif '/uclv' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://moodle.uclv.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 399
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de UCLV cargada...")

        elif '/uvs' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://uvs.ucm.cmw.sld.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 120
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Uvs cargada...")

        elif '/evea' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://evea.uh.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 200
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Evea cargada...")
        
        elif '/cursos' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://cursos.uo.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Cursos cargada...")
        
        elif '/eva' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eva.uo.edu.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---."
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Eva cargada...")
        
        elif "/artem" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "http://www.aulavirtual.art.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 90
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aula Artemisa cargada...")
            
        elif '/eduvirtual' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eduvirtual.uho.edu.cu/"
            getUser['uploadtype'] =  "blog"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 3
            getUser['zips'] = 8
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Eduvirtual cargada...")
        
        elif "/gtm" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulauvs.gtm.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 7
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aula Guantanamo cargada...")
        ###################################################     
  
        elif '/del_' in msgText and user_info['cloudtype']=='moodle':
            findex = int(str(msgText).split('_')[1])
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfile = client.getEvidences()[findex]
                client.deleteEvidence(evfile)
                client.logout()
                bot.editMessageText(message,'⊷𝙰𝚛𝚌𝚑𝚒𝚟𝚘 𝚎𝚕𝚒𝚖𝚒𝚗𝚊𝚍𝚘🗑️⊶')
            else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
        elif '/delall' in msgText and user_info['cloudtype']=='moodle':
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfiles = client.getEvidences()
                for item in evfiles:
                	client.deleteEvidence(item)
                client.logout()
                bot.editMessageText(message,'⊷𝙰𝚛𝚌𝚑𝚒𝚟𝚘𝚜 𝚎𝚕𝚒𝚖𝚒𝚗𝚊𝚍𝚘𝚜🗑️⊶')
            else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)

        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 14681595
            #    api_hash = 'a86730aab5c59953c424abb4396d32d5'
            #    bot_token = '5759495332:AAF5ZI9GOkTJ2yN7N7anruHsAvB8mdHH2-s'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'⊷⚠️𝙴𝚛𝚛𝚘𝚛, 𝚗𝚘 𝚜𝚎 𝚙𝚞𝚍𝚘 𝚊𝚗𝚊𝚕𝚒𝚣𝚊𝚛 𝚌𝚘𝚛𝚛𝚎𝚌𝚝𝚊𝚖𝚎𝚗𝚝𝚎⚠️⊶')
    except Exception as ex:
           print(str(ex))
           bot.sendMessage(update.message.chat.id,str(ex))
        

def main():
    bot_token = os.environ.get('5759495332:AAF5ZI9GOkTJ2yN7N7anruHsAvB8mdHH2-s')
    

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
