package org.freefinder.app

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import java.time.Instant

class MainActivity:ComponentActivity(){
    override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);setContent { FreeFinder() }}
}
@OptIn(ExperimentalMaterial3Api::class)
@Composable fun FreeFinder(vm:CatalogViewModel=viewModel()){
    val settings by vm.settings.collectAsStateWithLifecycle()
    val offers by vm.offers.collectAsStateWithLifecycle()
    val personal by vm.personal.collectAsStateWithLifecycle()
    val loading by vm.loading.collectAsStateWithLifecycle()
    val error by vm.error.collectAsStateWithLifecycle()
    val dark=when(settings.dark){"dark"->true;"light"->false;else->isSystemInDarkTheme()}
    val palette=if(dark) darkColorScheme(primary=Color(0xFF8DDEC0),secondary=Color(0xFFAFCBC0)) else lightColorScheme(primary=Color(0xFF166C53),secondary=Color(0xFF4C6359),background=Color(0xFFF6F8F5))
    val l=settings.lang;fun t(k:String)=tr(l,k)
    var tab by remember {mutableStateOf("catalog")}
    var filters by remember {mutableStateOf(Filters())}
    var filterDialog by remember {mutableStateOf(false)}
    var selected by remember {mutableStateOf<String?>(null)}
    val context=LocalContext.current
    val notificationPermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted->if(granted) Notices.send(context,"FreeFinder",t("test"),99) }
    val current=offers.find{it.id==selected}
    BackHandler(selected!=null){selected=null}
    MaterialTheme(colorScheme=palette){
        Scaffold(topBar={TopAppBar(title={Column { Text("FreeFinder",fontWeight=FontWeight.Bold);Text(if(current!=null) t(current.kind) else t(tab),style=MaterialTheme.typography.labelMedium) }},navigationIcon={if(current!=null) IconButton(onClick={selected=null}){Icon(Icons.Outlined.ArrowBack,t("back"))}},actions={if(tab=="catalog"&&current==null){IconButton(onClick={filterDialog=true}){Icon(Icons.Outlined.Tune,t("filters"))};IconButton(onClick=vm::sync,enabled=!loading){Icon(Icons.Outlined.Refresh,t("sync"))}}})},bottomBar={if(current==null) NavigationBar {listOf("catalog" to Icons.Outlined.Search,"favorites" to Icons.Outlined.FavoriteBorder,"history" to Icons.Outlined.History,"settings" to Icons.Outlined.Settings).forEach{(key,icon)->NavigationBarItem(selected=tab==key,onClick={tab=key},icon={Icon(icon,t(key))},label={Text(t(key))})}}}){padding->
            Column(Modifier.padding(padding).fillMaxSize()){
                if(loading) LinearProgressIndicator(Modifier.fillMaxWidth())
                if(error!=null) Surface(color=MaterialTheme.colorScheme.errorContainer){Text(error!!,Modifier.padding(12.dp),style=MaterialTheme.typography.bodySmall)}
                when {
                    current!=null->Detail(current,personal[current.id]?:Personal(current.id),l,vm)
                    tab=="settings"->SettingsScreen(settings,l,vm){notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)}
                    tab=="history"->LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
                        item{Text(t("last_sync")+": "+settings.lastSync.ifBlank{"—"});Text(t("server_note"),style=MaterialTheme.typography.bodySmall)}
                        val runs=runCatching{vm.repo.gson.fromJson(settings.runs,Array<SyncRun>::class.java).toList()}.getOrDefault(emptyList())
                        if(runs.isEmpty()) item{Text(t("no_runs"))}
                        items(runs,key={it.id}){r->Card(Modifier.fillMaxWidth()){Column(Modifier.padding(14.dp)){Text(r.source,fontWeight=FontWeight.Bold);Text("${r.status} · ${r.count}");Text(r.finishedAt?:r.startedAt,style=MaterialTheme.typography.bodySmall);r.error?.let{Text(it,color=MaterialTheme.colorScheme.error)}}}}
                        items(offers.filter{it.cachedOnly},key={"archived"+it.id}){o->OfferCard(o,personal[o.id]?.favorite==true,l,{selected=o.id},{vm.favorite(o.id)})}
                        items(personal.values.filter{it.state.isNotBlank()},key={"p"+it.id}){p->offers.find{it.id==p.id}?.let{o->Card(onClick={selected=o.id},modifier=Modifier.fillMaxWidth()){Column(Modifier.padding(12.dp)){Text(o.name);Text(t(p.state)+" · "+p.paid)}}}}
                    }
                    else->{
                        Row(Modifier.fillMaxWidth().padding(horizontal=16.dp,vertical=8.dp),verticalAlignment=Alignment.CenterVertically){
                            Column(Modifier.weight(1f)){Text(t("opportunities"),style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold);Text("${offers.count{!it.cachedOnly}} · "+t("observed"),style=MaterialTheme.typography.bodySmall)}
                            if(filters!=Filters()) TextButton(onClick={filters=Filters()}){Text(t("reset"))}
                        }
                        OutlinedTextField(value=filters.query,onValueChange={filters=filters.copy(query=it)},modifier=Modifier.fillMaxWidth().padding(horizontal=16.dp),placeholder={Text(t("search"))},leadingIcon={Icon(Icons.Outlined.Search,null)},singleLine=true)
                        LazyRow(contentPadding=PaddingValues(horizontal=16.dp),horizontalArrangement=Arrangement.spacedBy(8.dp)){item{FilterChip(selected=filters.category.isBlank(),onClick={filters=filters.copy(category="")},label={Text(t("all"))})};items(categories){c->FilterChip(selected=filters.category==c,onClick={filters=filters.copy(category=c)},label={Text(t(c))})}}
                        LazyRow(contentPadding=PaddingValues(horizontal=16.dp),horizontalArrangement=Arrangement.spacedBy(8.dp)){items(listOf("","ES","AD","both","pickup")){c->FilterChip(selected=filters.country==c,onClick={filters=filters.copy(country=c)},label={Text(when(c){""->t("all");"both"->"ES + AD";"pickup"->t("pickup");else->c})})}}
                        val filtered=offers.filter{filters.matches(it)&&(if(tab=="favorites")personal[it.id]?.favorite==true else !it.cachedOnly)}
                        val sorted=when(filters.sort){"ending"->filtered.sortedBy{it.endsAt?:"9999"};"total"->filtered.sortedBy{if(filters.country=="AD")it.totalAd?:Double.MAX_VALUE else it.totalEs?:Double.MAX_VALUE};"value"->filtered.sortedByDescending{it.regularPrice?:-1.0};"confidence"->filtered.sortedByDescending{it.confidence};else->filtered.sortedByDescending{it.discoveredAt}}
                        LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
                            item{Text("${sorted.size} "+t("results"),style=MaterialTheme.typography.labelLarge);Text(t(if(filters.includeUnknown)"unknown_note" else "country_note"),style=MaterialTheme.typography.bodySmall)}
                            if(sorted.isEmpty()) item{Card{Column(Modifier.padding(24.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){Icon(Icons.Outlined.TravelExplore,null,Modifier.size(40.dp));Text(t(if(offers.isEmpty()) "empty" else "empty_filters"));if(offers.isNotEmpty()) TextButton(onClick={filters=Filters()}){Text(t("reset"))};Button(onClick=vm::sync,enabled=!loading){Text(t("sync"))}}}}
                            items(sorted,key={it.id}){o->OfferCard(o,personal[o.id]?.favorite==true,l,{selected=o.id},{vm.favorite(o.id)})}
                        }
                    }
                }
            }
        }
        if(filterDialog) AlertDialog(onDismissRequest={filterDialog=false},confirmButton={TextButton(onClick={filterDialog=false}){Text(t("close"))}},title={Text(t("filters"))},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(10.dp)){
            Choice(t("sort"),listOf("newest","ending","total","value","confidence"),filters.sort,{t(it)}){filters=filters.copy(sort=it)}
            Choice(t("brand"),listOf("")+offers.mapNotNull{it.brand}.distinct().sorted(),filters.brand,{if(it.isBlank())t("all") else it}){filters=filters.copy(brand=it)}
            Choice(t("platform"),listOf("")+offers.map{it.platform}.distinct().sorted(),filters.platform,{if(it.isBlank())t("all") else it}){filters=filters.copy(platform=it)}
            Choice(t("availability"),listOf("","verified","conditional","pending","sold_out","expired"),filters.status,{if(it.isBlank())t("all") else t(it)}){filters=filters.copy(status=it)}
            Row(verticalAlignment=Alignment.CenterVertically){Checkbox(filters.includeUnknown,{filters=filters.copy(includeUnknown=it)});Text(t("include_unknown"))}
            Choice(t("filters"),listOf("")+kinds,filters.kind,{if(it.isBlank())t("all") else t(it)}){filters=filters.copy(kind=it)}
            OutlinedTextField(value=filters.maxShipping?.toString()?:"",onValueChange={filters=filters.copy(maxShipping=it.toDoubleOrNull()?.coerceAtLeast(0.0))},label={Text(t("max_shipping"))})
            Row(verticalAlignment=Alignment.CenterVertically){Checkbox(filters.keepOnly,{filters=filters.copy(keepOnly=it)});Text(t("keep"))}
        }})
    }
}
@Composable fun Choice(label:String,options:List<String>,value:String,render:(String)->String,onChange:(String)->Unit){
    var expanded by remember{mutableStateOf(false)}
    Column {Text(label,style=MaterialTheme.typography.labelMedium);Box{OutlinedButton(onClick={expanded=true}){Text(render(value))};DropdownMenu(expanded=expanded,onDismissRequest={expanded=false}){options.forEach{o->DropdownMenuItem(text={Text(render(o))},onClick={onChange(o);expanded=false})}}}}
}
fun money(v:Double?,currency:String)=v?.let{String.format(java.util.Locale.getDefault(),"%.2f %s",it,currency)}?:"—"
@Composable fun OfferCard(o:Offer,favorite:Boolean,l:String,open:()->Unit,toggle:()->Unit){
    Card(onClick=open,modifier=Modifier.fillMaxWidth()){
        if(o.imageUrl!=null) AsyncImage(model=o.imageUrl,contentDescription=o.name,contentScale=ContentScale.Fit,modifier=Modifier.fillMaxWidth().height(220.dp).background(Color.White))
        else Box(Modifier.fillMaxWidth().height(100.dp).background(MaterialTheme.colorScheme.secondaryContainer),contentAlignment=Alignment.Center){Column(horizontalAlignment=Alignment.CenterHorizontally){Icon(Icons.Outlined.Inventory2,null,Modifier.size(36.dp));Text(tr(l,"no_photo"),style=MaterialTheme.typography.labelSmall)}}
        Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
            Row(verticalAlignment=Alignment.CenterVertically){Text(o.name,Modifier.weight(1f),style=MaterialTheme.typography.titleMedium);IconButton(onClick=toggle){Icon(if(favorite)Icons.Outlined.Favorite else Icons.Outlined.FavoriteBorder,tr(l,"favorites"))}}
            if(o.sourceStatus=="missing"||o.sourceStatus=="unreachable") Text(tr(l,"stale_source"),color=MaterialTheme.colorScheme.error)
            if(o.cachedOnly) Text(tr(l,"cached_only"),color=MaterialTheme.colorScheme.error)
            Text(o.platform,style=MaterialTheme.typography.labelMedium)
            o.imageCredit?.let{Text(it+" · "+o.imageLicense.orEmpty(),style=MaterialTheme.typography.labelSmall)}
            if(o.regularPrice!=null) Text(money(o.regularPrice,o.currency),textDecoration=TextDecoration.LineThrough)
            Text(money(o.promoPrice,o.currency),style=MaterialTheme.typography.headlineSmall,color=MaterialTheme.colorScheme.primary,fontWeight=FontWeight.Bold)
            Text(tr(l,o.kind)+" · "+tr(l,o.status),style=MaterialTheme.typography.labelLarge)
            Text("ES: ${tr(l,o.shippingEs)} · AD: ${tr(l,o.shippingAd)}",style=MaterialTheme.typography.bodySmall)
            Text(tr(l,"shipping")+": "+if(o.shippingCostEs==null)tr(l,"cart") else money(o.shippingCostEs,o.currency),style=MaterialTheme.typography.bodySmall)
            if(o.additionalChargesEs!=null) Text(tr(l,"charges")+": "+money(o.additionalChargesEs,o.currency),color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall)
            Text(tr(l,"checked")+": "+o.checkedAt,style=MaterialTheme.typography.labelSmall)
        }
    }
}
@Composable fun Detail(o:Offer,p:Personal,l:String,vm:CatalogViewModel){
    val context=LocalContext.current
    var notes by remember(o.id,p.notes){mutableStateOf(p.notes)};var paid by remember(o.id,p.paid){mutableStateOf(p.paid)};var date by remember(o.id,p.requestedAt){mutableStateOf(p.requestedAt)}
    LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{OfferCard(o,p.favorite,l,{}, {vm.favorite(o.id)})}
        item{Text(o.description);Text(tr(l,"not_claimed"),color=MaterialTheme.colorScheme.error)}
        item{Button(onClick={runCatching{val uri=Uri.parse(o.requestUrl?:o.url);if(uri.scheme=="https")context.startActivity(Intent(Intent.ACTION_VIEW,uri))}}){Text(tr(l,"open"))}}
        item{listOf("ES","AD").forEach{c->Text("$c · ${tr(l,"shipping")}: "+money(if(c=="ES")o.shippingCostEs else o.shippingCostAd,o.currency));Text(tr(l,"charges")+": "+money(if(c=="ES")o.additionalChargesEs else o.additionalChargesAd,o.currency));Text(tr(l,"total")+": "+money(if(c=="ES")o.totalEs else o.totalAd,o.currency))}}
        item{Text(tr(l,"conditions"),style=MaterialTheme.typography.titleMedium);o.requirements.forEach{Text("• $it")};o.residency?.let{Text(it)};o.endsAt?.let{Text(it)}}
        if(o.riskReasons.isNotEmpty())item{Text(tr(l,"risk"),style=MaterialTheme.typography.titleMedium);o.riskReasons.forEach{Text(it)}}
        item{Text(tr(l,"evidence"),style=MaterialTheme.typography.titleMedium);o.evidence.forEach{e->Text("${e.checkedAt}\n${e.field}: ${e.note}\n${e.source}",style=MaterialTheme.typography.bodySmall)}}
        item{Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){FilterChip(p.state=="requested",{vm.personal(p.copy(state="requested",requestedAt=Instant.now().toString()))},{Text(tr(l,"requested"))});FilterChip(p.state=="received",{vm.personal(p.copy(state="received"))},{Text(tr(l,"received"))})}}
        item{OutlinedTextField(notes,{notes=it.take(4000)},label={Text(tr(l,"notes"))},modifier=Modifier.fillMaxWidth());OutlinedTextField(paid,{paid=it.take(60)},label={Text(tr(l,"paid"))},modifier=Modifier.fillMaxWidth());OutlinedTextField(date,{date=it.take(60)},label={Text(tr(l,"date"))},modifier=Modifier.fillMaxWidth());Button(onClick={vm.personal(p.copy(notes=notes,paid=paid,requestedAt=date))}){Text(tr(l,"save_personal"))}}
    }
}
@Composable fun SettingsScreen(s:Settings,l:String,vm:CatalogViewModel,test:()->Unit){
    var draft by remember(s){mutableStateOf(s)}
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        Text(tr(l,"server_note"),style=MaterialTheme.typography.bodySmall)
        Card{Text(tr(l,"coverage"),Modifier.padding(16.dp),style=MaterialTheme.typography.bodySmall)}
        OutlinedTextField(draft.url,{draft=draft.copy(url=it)},label={Text(tr(l,"url"))},placeholder={Text("https://freefinder.example/")},modifier=Modifier.fillMaxWidth(),singleLine=true)
        Choice(tr(l,"language"),listOf("es","ca","en"),draft.lang,{when(it){"es"->"Castellano";"ca"->"Català";else->"English"}}){draft=draft.copy(lang=it)}
        Choice(tr(l,"theme"),listOf("system","light","dark"),draft.dark,{tr(l,it)}){draft=draft.copy(dark=it)}
        Choice(tr(l,"hours"),listOf("0","1","3","6","12","24"),draft.hours.toString(),{if(it=="0")tr(l,"manual") else "$it h"}){draft=draft.copy(hours=it.toInt())}
        Row(verticalAlignment=Alignment.CenterVertically){Switch(draft.notifications,{draft=draft.copy(notifications=it)});Text(tr(l,"notifications"),Modifier.padding(start=8.dp))}
        Row(verticalAlignment=Alignment.CenterVertically){Switch(draft.night,{draft=draft.copy(night=it)});Text(tr(l,"night"),Modifier.padding(start=8.dp))}
        Choice(tr(l,"notify_category"),listOf("")+categories,draft.notifyCategory,{if(it.isBlank())tr(l,"all") else tr(l,it)}){draft=draft.copy(notifyCategory=it)}
        Choice(tr(l,"notify_country"),listOf("","ES","AD"),draft.notifyCountry,{if(it.isBlank())tr(l,"all") else it}){draft=draft.copy(notifyCountry=it)}
        OutlinedTextField(draft.postcode,{draft=draft.copy(postcode=it.take(80))},label={Text(tr(l,"postcode"))},modifier=Modifier.fillMaxWidth());Text(tr(l,"postal_note"),style=MaterialTheme.typography.bodySmall)
        Button(onClick={vm.save(draft)}){Text(tr(l,"save"))}
        OutlinedButton(onClick=test){Text(tr(l,"test"))}
        Text("FreeFinder 0.2.0 · Android 14+",style=MaterialTheme.typography.labelSmall)
    }
}
