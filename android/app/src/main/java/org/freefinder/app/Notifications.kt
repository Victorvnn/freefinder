package org.freefinder.app

import android.Manifest
import android.app.*
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.flow.first
import java.util.concurrent.TimeUnit

object Notices {
    fun send(context:Context,title:String,text:String,id:Int=1){
        if(context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED) return
        val manager=context.getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel("offers","FreeFinder",NotificationManager.IMPORTANCE_DEFAULT))
        val intent=PendingIntent.getActivity(context,0,Intent(context,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        manager.notify(id,NotificationCompat.Builder(context,"offers").setSmallIcon(R.drawable.ic_freefinder_mark).setContentTitle(title).setContentText(text).setContentIntent(intent).setAutoCancel(true).build())
    }
    fun schedule(context:Context,hours:Int){
        val manager=WorkManager.getInstance(context)
        if(hours==0){manager.cancelUniqueWork("sync");return}
        val req=PeriodicWorkRequestBuilder<SyncWorker>(hours.toLong(),TimeUnit.HOURS).setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()).setBackoffCriteria(BackoffPolicy.EXPONENTIAL,30,TimeUnit.SECONDS).build()
        manager.enqueueUniquePeriodicWork("sync",ExistingPeriodicWorkPolicy.UPDATE,req)
    }
}
class SyncWorker(context:Context,params:WorkerParameters):CoroutineWorker(context,params){
    override suspend fun doWork():Result {
        val repo=(applicationContext as FreeFinderApp).repo
        return try {
            val settings=repo.prefs.flow.first()
            if(settings.url.isBlank()) return Result.success()
            val fresh=repo.sync()
            val h=java.time.LocalTime.now().hour
            val matching=fresh.filter {(settings.notifyCategory.isBlank()||it.category==settings.notifyCategory)&&(settings.notifyCountry.isBlank()||if(settings.notifyCountry=="AD")it.shippingAd=="confirmed" else it.shippingEs=="confirmed")}
            if(settings.notifications&&matching.isNotEmpty()&&(!settings.night||h in 8..21)){
                Notices.send(applicationContext,"FreeFinder", "${matching.size} ${tr(settings.lang,"new_offers")}")
            }
            Result.success()
        }catch(e:Exception){if(runAttemptCount<3) Result.retry() else Result.failure()}
    }
}
