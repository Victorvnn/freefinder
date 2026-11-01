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
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items as gridItems
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel

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
    val palette=if(dark) darkColorScheme(primary=Color(0xFF91E3B8),onPrimary=Color(0xFF073825),primaryContainer=Color(0xFF154C38),onPrimaryContainer=Color(0xFFC2F8D9),secondary=Color(0xFFACCDBB),secondaryContainer=Color(0xFF2A4236),onSecondaryContainer=Color(0xFFDFECE2),background=Color(0xFF0C1511),surface=Color(0xFF16241D),surfaceVariant=Color(0xFF2C3B32),onSurfaceVariant=Color(0xFFB6C5BA),outline=Color(0xFF819487)) else lightColorScheme(primary=Color(0xFF146341),onPrimary=Color.White,primaryContainer=Color(0xFFDCF4E3),onPrimaryContainer=Color(0xFF0A3825),secondary=Color(0xFF4D6D58),secondaryContainer=Color(0xFFE8EEE3),onSecondaryContainer=Color(0xFF2D4935),background=Color(0xFFF3F6F0),surface=Color(0xFFFFFFFF),surfaceVariant=Color(0xFFE6ECE3),onSurfaceVariant=Color(0xFF536658),outline=Color(0xFF819487))
    val l=settings.lang;fun t(k:String)=tr(l,k)
    var tab by remember {mutableStateOf("catalog")}
    var filters by remember {mutableStateOf(Filters())}
    var filterDialog by remember {mutableStateOf(false)}
    var selected by remember {mutableStateOf<String?>(null)}
    val context=LocalContext.current
    val notificationPermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted->if(granted) Notices.send(context,"FreeFinder",t("test"),99) }
    val current=offers.find{it.id==selected}
    BackHandler(selected!=null){selected=null}
    SideEffect {
        val activity=context as? android.app.Activity
        activity?.window?.let{window->
            androidx.core.view.WindowCompat.getInsetsController(window,window.decorView).apply{
                isAppearanceLightStatusBars=!dark
                isAppearanceLightNavigationBars=!dark
            }
            @Suppress("DEPRECATION")
            run { window.statusBarColor=palette.background.toArgb();window.navigationBarColor=palette.background.toArgb() }
            window.isNavigationBarContrastEnforced=false
        }
    }
    MaterialTheme(colorScheme=palette,shapes=Shapes(small=RoundedCornerShape(10.dp),medium=RoundedCornerShape(18.dp),large=RoundedCornerShape(26.dp))){
        Scaffold(topBar={TopAppBar(title={Row(verticalAlignment=Alignment.CenterVertically){Icon(painterResource(R.drawable.ic_freefinder_mark),null,Modifier.size(44.dp),tint=MaterialTheme.colorScheme.primary);Spacer(Modifier.width(10.dp));Column { Text("FreeFinder",fontWeight=FontWeight.Bold);Text(if(current!=null) t(current.kind) else t(tab),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onSurfaceVariant) }}},navigationIcon={if(current!=null) IconButton(onClick={selected=null}){Icon(Icons.Outlined.ArrowBack,t("back"))}},actions={if(tab in listOf("catalog","favorites")&&current==null){IconButton(onClick={filterDialog=true}){Icon(Icons.Outlined.Tune,t("filters"))};IconButton(onClick=vm::sync,enabled=!loading){Icon(Icons.Outlined.Refresh,t("sync"))}}})},bottomBar={if(current==null) NavigationBar(containerColor=MaterialTheme.colorScheme.surface) {listOf("catalog" to Icons.Outlined.Search,"favorites" to Icons.Outlined.FavoriteBorder,"sources" to Icons.Outlined.TravelExplore,"history" to Icons.Outlined.History,"settings" to Icons.Outlined.Settings).forEach{(key,icon)->NavigationBarItem(selected=tab==key,onClick={tab=key},icon={Icon(icon,t(key))},label={Text(t(key),maxLines=1,style=MaterialTheme.typography.labelSmall)})}}}){padding->
            Column(Modifier.padding(padding).fillMaxSize()){
                if(loading) LinearProgressIndicator(Modifier.fillMaxWidth())
                if(error!=null) Surface(color=MaterialTheme.colorScheme.errorContainer){Text(error!!,Modifier.padding(12.dp),style=MaterialTheme.typography.bodySmall)}
                when {
                    current!=null->Detail(current,personal[current.id]?:Personal(current.id),l,vm)
                    tab=="settings"->SettingsScreen(settings,l,vm){notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)}
                    tab=="sources"->SourcesScreen(runCatching{vm.repo.gson.fromJson(settings.sources,Array<Source>::class.java).toList()}.getOrDefault(emptyList()),l)
                    tab=="history"->LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
                        item{Text(t("last_sync")+": "+readableDate(settings.lastSync));Text(t("server_note"),style=MaterialTheme.typography.bodySmall)}
                        val runs=runCatching{vm.repo.gson.fromJson(settings.runs,Array<SyncRun>::class.java).toList()}.getOrDefault(emptyList())
                        if(runs.isEmpty()) item{Text(t("no_runs"))}
                        items(runs,key={it.id}){r->Card(Modifier.fillMaxWidth()){Column(Modifier.padding(14.dp)){Text(r.source,fontWeight=FontWeight.Bold);Text("${r.status} · ${r.count}");Text(readableDate(r.finishedAt?:r.startedAt),style=MaterialTheme.typography.bodySmall);r.error?.let{Text(it,color=MaterialTheme.colorScheme.error)}}}}
                        items(offers.filter{it.cachedOnly},key={"archived"+it.id}){o->OfferCard(o,personal[o.id]?.favorite==true,l,{selected=o.id},{vm.favorite(o.id)})}
                        items(personal.values.filter{it.state.isNotBlank()},key={"p"+it.id}){p->offers.find{it.id==p.id}?.let{o->Card(onClick={selected=o.id},modifier=Modifier.fillMaxWidth()){Column(Modifier.padding(12.dp)){Text(o.name);Text(t(p.state)+" · "+p.paid)}}}}
                    }
                    else->{
                        val filtered=offers.filter{filters.matches(it)&&(if(tab=="favorites")personal[it.id]?.favorite==true else !it.cachedOnly)}
                        val sorted=when(filters.sort){"ending"->filtered.sortedBy{it.endsAt?:"9999"};"total"->filtered.sortedBy{if(filters.country=="AD")it.totalAd?:Double.MAX_VALUE else it.totalEs?:Double.MAX_VALUE};"value"->filtered.sortedByDescending{it.regularPrice?:-1.0};"confidence"->filtered.sortedByDescending{it.confidence};else->filtered.sortedByDescending{it.discoveredAt}}
                        val columns=if(LocalDensity.current.fontScale>1.2f)GridCells.Fixed(1) else GridCells.Adaptive(165.dp)
                        LazyVerticalGrid(columns=columns,contentPadding=PaddingValues(16.dp),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
                            item(span={GridItemSpan(maxLineSpan)}){CatalogHero(if(tab=="favorites")personal.values.count{it.favorite} else offers.count{!it.cachedOnly},settings.lastSync,l)}
                            item(span={GridItemSpan(maxLineSpan)}){OutlinedTextField(value=filters.query,onValueChange={filters=filters.copy(query=it)},modifier=Modifier.fillMaxWidth(),placeholder={Text(t("search"))},leadingIcon={Icon(Icons.Outlined.Search,null)},trailingIcon={if(filters.query.isNotEmpty())IconButton(onClick={filters=filters.copy(query="")}){Icon(Icons.Outlined.Close,t("reset"))}},shape=RoundedCornerShape(20.dp),singleLine=true)}
                            item(span={GridItemSpan(maxLineSpan)}){LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)){
                                item{FilterChip(selected=filters.category.isBlank(),onClick={filters=filters.copy(category="")},leadingIcon={Icon(Icons.Outlined.Apps,null,Modifier.size(18.dp))},label={Text(t("all"))})}
                                items(categories){c->FilterChip(selected=filters.category==c,onClick={filters=filters.copy(category=c)},leadingIcon={Icon(categoryIcon(c),null,Modifier.size(18.dp))},label={Text(t(c))})}
                            }}
                            item(span={GridItemSpan(maxLineSpan)}){LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)){items(listOf("","ES","AD","both","pickup")){c->FilterChip(selected=filters.country==c,onClick={filters=filters.copy(country=c)},label={Text(when(c){""->t("all_destinations");"both"->"ES + AD";"pickup"->t("pickup");else->c})})}}}
                            item(span={GridItemSpan(maxLineSpan)}){Column(verticalArrangement=Arrangement.spacedBy(5.dp)){
                                Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){Text("${sorted.size} "+t("results"),Modifier.weight(1f),style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold);if(filters!=Filters())TextButton(onClick={filters=Filters()}){Text(t("reset"))};TextButton(onClick={tab="sources"}){Text(t("sources"));Icon(Icons.Outlined.ArrowForward,null,Modifier.size(16.dp))}}
                                if(filters.country.isNotBlank())Text(t(if(filters.includeUnknown)"unknown_note" else "country_note"),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                            }}
                            if(sorted.isEmpty())item(span={GridItemSpan(maxLineSpan)}){Card{Column(Modifier.fillMaxWidth().padding(26.dp),verticalArrangement=Arrangement.spacedBy(14.dp),horizontalAlignment=Alignment.CenterHorizontally){Icon(Icons.Outlined.TravelExplore,null,Modifier.size(42.dp));Text(t(if(offers.isEmpty())"empty" else "empty_filters"));if(offers.isNotEmpty())TextButton(onClick={filters=Filters()}){Text(t("reset"))};Button(onClick=vm::sync,enabled=!loading){Text(t("sync"))}}}}
                            gridItems(sorted,key={it.id}){o->ProductTile(o,personal[o.id]?.favorite==true,l,filters.country,{selected=o.id},{vm.favorite(o.id)})}
                            item(span={GridItemSpan(maxLineSpan)}){Text(t("catalog_footer"),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant,modifier=Modifier.padding(vertical=12.dp))}
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
    Card(onClick=open,modifier=Modifier.fillMaxWidth(),shape=RoundedCornerShape(26.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface)){
        ProductPhoto(o,l,300)
        Column(Modifier.padding(20.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
            Row(verticalAlignment=Alignment.CenterVertically){Text(o.platform,Modifier.weight(1f),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary);IconButton(onClick=toggle){Icon(if(favorite)Icons.Outlined.Favorite else Icons.Outlined.FavoriteBorder,tr(l,"favorites"),tint=MaterialTheme.colorScheme.primary)}}
            Text(o.name,style=MaterialTheme.typography.headlineSmall,fontWeight=FontWeight.Bold)
            StatusPill(o.status,l)
            if(o.sourceStatus in listOf("missing","unreachable"))Text(tr(l,"stale_source"),color=MaterialTheme.colorScheme.error)
            if(o.cachedOnly)Text(tr(l,"cached_only"),color=MaterialTheme.colorScheme.error)
            if(o.regularPrice!=null)Text(money(o.regularPrice,o.currency),textDecoration=TextDecoration.LineThrough)
            Text(money(o.promoPrice,o.currency),style=MaterialTheme.typography.headlineLarge,fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.primary)
            Text(tr(l,o.kind),style=MaterialTheme.typography.titleSmall)
            Text("ES: ${tr(l,o.shippingEs)} · AD: ${tr(l,o.shippingAd)}",style=MaterialTheme.typography.bodySmall)
            o.imageCredit?.let{Text(it+" · "+o.imageLicense.orEmpty(),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}
            Text(tr(l,"checked")+" · "+readableDate(o.checkedAt),style=MaterialTheme.typography.labelSmall)
        }
    }
}
@Composable fun Detail(o:Offer,p:Personal,l:String,vm:CatalogViewModel){
    val context=LocalContext.current
    var notes by remember(o.id,p.notes){mutableStateOf(p.notes)};var paid by remember(o.id,p.paid){mutableStateOf(p.paid)};var date by remember(o.id,p.requestedAt){mutableStateOf(p.requestedAt)}
    LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{OfferCard(o,p.favorite,l,{}, {vm.favorite(o.id)})}
        item{Text(o.description);Text(tr(l,"not_claimed"),color=MaterialTheme.colorScheme.error)}
        if(o.imageLicenseUrl!=null)item{TextButton(onClick={runCatching{val uri=Uri.parse(o.imageLicenseUrl);if(uri.scheme=="https")context.startActivity(Intent(Intent.ACTION_VIEW,uri))}}){Icon(Icons.Outlined.Copyright,null,Modifier.size(18.dp));Spacer(Modifier.width(6.dp));Text(tr(l,"image_license"))}}
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
        Text("FreeFinder ${BuildConfig.VERSION_NAME} · Android 14+",style=MaterialTheme.typography.labelSmall)
    }
}
