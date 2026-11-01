package org.freefinder.app

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import androidx.room.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import com.google.gson.Gson

@Entity(tableName="offers") data class CachedOffer(@PrimaryKey val id:String,val json:String)
@Entity(tableName="personal") data class Personal(@PrimaryKey val id:String,val favorite:Boolean=false,val state:String="",val requestedAt:String="",val paid:String="",val notes:String="")
@Dao interface CatalogDao {
    @Query("SELECT * FROM offers") fun observeOffers():Flow<List<CachedOffer>>
    @Query("SELECT * FROM offers") suspend fun offers():List<CachedOffer>
    @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun insert(items:List<CachedOffer>)
    @Query("DELETE FROM offers") suspend fun clearOffers()
    @Query("SELECT * FROM personal") fun observePersonal():Flow<List<Personal>>
    @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun save(p:Personal)
}
@Database(entities=[CachedOffer::class,Personal::class],version=1,exportSchema=false)
abstract class CatalogDb:RoomDatabase(){ abstract fun dao():CatalogDao }
val Context.dataStore by preferencesDataStore("settings")
data class Settings(val url:String="https://victorvnn.github.io/freefinder/",val lang:String="es",val hours:Int=6,val dark:String="system",val notifications:Boolean=true,val night:Boolean=true,val notifyCategory:String="",val notifyCountry:String="",val postcode:String="",val lastSync:String="",val runs:String="[]",val sources:String="[]")
class Preferences(private val context:Context){
    val flow=context.dataStore.data.map { p->Settings(p[stringPreferencesKey("url")]?.takeIf{it.isNotBlank()}?:"https://victorvnn.github.io/freefinder/",p[stringPreferencesKey("lang")]?:"es",p[intPreferencesKey("hours")]?:6,p[stringPreferencesKey("dark")]?:"system",p[booleanPreferencesKey("notifications")]?:true,p[booleanPreferencesKey("night")]?:true,p[stringPreferencesKey("notifyCategory")]?:"",p[stringPreferencesKey("notifyCountry")]?:"",p[stringPreferencesKey("postcode")]?:"",p[stringPreferencesKey("lastSync")]?:"",p[stringPreferencesKey("runs")]?:"[]",p[stringPreferencesKey("sources")]?:"[]") }
    suspend fun save(s:Settings){context.dataStore.edit { p->
        p[stringPreferencesKey("url")]=s.url;p[stringPreferencesKey("lang")]=s.lang;p[intPreferencesKey("hours")]=s.hours;p[stringPreferencesKey("dark")]=s.dark;p[booleanPreferencesKey("notifications")]=s.notifications;p[booleanPreferencesKey("night")]=s.night;p[stringPreferencesKey("notifyCategory")]=s.notifyCategory;p[stringPreferencesKey("notifyCountry")]=s.notifyCountry;p[stringPreferencesKey("postcode")]=s.postcode
    }}
    suspend fun synced(runs:String,sources:String?=null){context.dataStore.edit { p->p[stringPreferencesKey("lastSync")]=java.time.Instant.now().toString();p[stringPreferencesKey("runs")]=runs;if(sources!=null)p[stringPreferencesKey("sources")]=sources }}
}
