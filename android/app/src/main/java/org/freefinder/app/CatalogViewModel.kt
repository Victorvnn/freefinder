package org.freefinder.app

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class CatalogViewModel(app:Application):AndroidViewModel(app){
    val repo=(app as FreeFinderApp).repo
    val settings=repo.prefs.flow.stateIn(viewModelScope,SharingStarted.Eagerly,Settings())
    val offers=repo.dao.observeOffers().map { items->items.mapNotNull { runCatching { repo.gson.fromJson(it.json,Offer::class.java) }.getOrNull() } }.stateIn(viewModelScope,SharingStarted.Eagerly,emptyList())
    val personal=repo.dao.observePersonal().map { it.associateBy { p->p.id } }.stateIn(viewModelScope,SharingStarted.Eagerly,emptyMap())
    val loading=MutableStateFlow(false);val error=MutableStateFlow<String?>(null)
    init { viewModelScope.launch {
        val first=repo.prefs.flow.first()
        Notices.schedule(getApplication(),first.hours)
        if(first.lastSync.isBlank())sync()
    }}
    fun sync(){if(loading.value)return;viewModelScope.launch {loading.value=true;error.value=null
        try{repo.sync()}catch(e:Exception){error.value=e.message?:"Connection error"}finally{loading.value=false}
    }}
    fun save(s:Settings){viewModelScope.launch{try{if(s.url.isNotBlank()) repo.api(s.url); repo.prefs.save(s);Notices.schedule(getApplication(),s.hours);error.value=null}catch(e:Exception){error.value=e.message}}}
    fun personal(p:Personal){viewModelScope.launch {repo.dao.save(p)}}
    fun favorite(id:String){val p=personal.value[id]?:Personal(id);personal(p.copy(favorite=!p.favorite))}
}
