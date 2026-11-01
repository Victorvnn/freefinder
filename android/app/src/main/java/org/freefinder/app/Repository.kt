package org.freefinder.app

import android.app.Application
import androidx.room.Room
import androidx.room.withTransaction
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query
import java.net.URI
import java.util.concurrent.TimeUnit

interface CatalogApi {
    @GET("v1/offers") suspend fun offers(@Query("limit") limit:Int=100,@Query("offset") offset:Int=0):Page
    @GET("v1/runs") suspend fun runs():List<SyncRun>
}
class Repository(app:Application){
    val db=Room.databaseBuilder(app,CatalogDb::class.java,"freefinder.db").build()
    val dao=db.dao();val prefs=Preferences(app);val gson=Gson()
    private val mutex=kotlinx.coroutines.sync.Mutex()
    fun api(url:String):CatalogApi {
        val uri=URI(url.trim())
        require(uri.host!=null && uri.userInfo==null && uri.query==null && uri.fragment==null && (uri.scheme=="https"||(BuildConfig.DEBUG&&uri.scheme=="http"))) {"HTTPS URL required"}
        val client=OkHttpClient.Builder().connectTimeout(15,TimeUnit.SECONDS).readTimeout(30,TimeUnit.SECONDS).followRedirects(false).followSslRedirects(false).build()
        return Retrofit.Builder().baseUrl(url.trim().trimEnd('/')+"/").client(client).addConverterFactory(GsonConverterFactory.create()).build().create(CatalogApi::class.java)
    }
    suspend fun sync():List<Offer> = withContext(Dispatchers.IO){
        mutex.lock()
        try {
            val settings=prefs.flow.first();require(settings.url.isNotBlank()) {"Backend URL required"}
            val service=api(settings.url);val collected=mutableListOf<Offer>();var offset=0
            do {val page=service.offers(offset=offset);collected.addAll(page.items);offset+=page.items.size
                require(offset<=10000){"Catalog exceeds local limit"}
                if(page.items.isEmpty()||offset>=page.total) break
            }while(true)
            val runs=service.runs()
            val oldRows=dao.offers()
            val old=oldRows.map { it.id }.toSet()
            val seen=collected.map{it.id}.toSet()
            val archived=oldRows.filter { it.id !in seen }.map { row->CachedOffer(row.id,gson.toJson(gson.fromJson(row.json,Offer::class.java).copy(cachedOnly=true))) }
            // Retain disappeared and expired entries locally for personal history.
            db.withTransaction {dao.insert(archived+collected.map { CachedOffer(it.id,gson.toJson(it.copy(cachedOnly=false))) })}
            prefs.synced(gson.toJson(runs))
            collected.filter { it.id !in old }
        } finally {mutex.unlock()}
    }
}
class FreeFinderApp:Application(){val repo by lazy {Repository(this)}}
