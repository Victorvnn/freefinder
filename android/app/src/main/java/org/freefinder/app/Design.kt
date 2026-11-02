package org.freefinder.app

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.SubcomposeAsyncImage
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

fun readableDate(value:String):String=runCatching {
    DateTimeFormatter.ofPattern("dd MMM · HH:mm",Locale.getDefault()).withZone(ZoneId.systemDefault()).format(Instant.parse(value))
}.getOrDefault(value.ifBlank{"—"})

fun categoryIcon(category:String):ImageVector=when(category){
    "electronics"->Icons.Outlined.Devices;"computing"->Icons.Outlined.Computer
    "appliances"->Icons.Outlined.Kitchen;"home"->Icons.Outlined.Home
    "tools"->Icons.Outlined.Handyman;"clothing"->Icons.Outlined.Checkroom
    "shoes"->Icons.Outlined.Hiking;"accessories"->Icons.Outlined.Watch
    "beauty"->Icons.Outlined.Face;"hygiene"->Icons.Outlined.Soap
    "food"->Icons.Outlined.Restaurant;"pets"->Icons.Outlined.Pets
    "sport"->Icons.Outlined.FitnessCenter;"automotive"->Icons.Outlined.DirectionsCar
    "office"->Icons.Outlined.Description;"garden"->Icons.Outlined.LocalFlorist
    "children"->Icons.Outlined.ChildCare;else->Icons.Outlined.Category
}

@Composable fun CatalogHero(count:Int,lastSync:String,l:String){
    Surface(color=MaterialTheme.colorScheme.primaryContainer,shape=RoundedCornerShape(28.dp),modifier=Modifier.fillMaxWidth()){
        Column(Modifier.padding(22.dp),verticalArrangement=Arrangement.spacedBy(9.dp)){
            Row(verticalAlignment=Alignment.CenterVertically){
                Surface(shape=CircleShape,color=MaterialTheme.colorScheme.primary){Icon(Icons.Outlined.AutoAwesome,null,Modifier.padding(8.dp).size(18.dp),tint=MaterialTheme.colorScheme.onPrimary)}
                Spacer(Modifier.width(9.dp));Text(tr(l,"hero_eyebrow"),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.onPrimaryContainer)
            }
            Text(tr(l,"hero_title"),style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.onPrimaryContainer)
            Text("$count "+tr(l,"observed"),style=MaterialTheme.typography.bodyMedium,color=MaterialTheme.colorScheme.onPrimaryContainer)
            if(lastSync.isNotBlank())Text(tr(l,"last_sync")+" · "+readableDate(lastSync),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onPrimaryContainer)
        }
    }
}

@Composable fun StatusPill(status:String,l:String){
    val good=status=="verified"
    val bad=status in listOf("expired","sold_out","rejected")
    Surface(shape=RoundedCornerShape(8.dp),color=when{good->MaterialTheme.colorScheme.primaryContainer;bad->MaterialTheme.colorScheme.errorContainer;else->MaterialTheme.colorScheme.secondaryContainer}){
        Text(tr(l,status),Modifier.padding(horizontal=9.dp,vertical=5.dp),style=MaterialTheme.typography.labelSmall,fontWeight=FontWeight.SemiBold,maxLines=2)
    }
}

@Composable fun ProductPhoto(o:Offer,l:String,height:Int=190){
    Box(Modifier.fillMaxWidth().height(height.dp).background(Color(0xFFFFFFFF)),contentAlignment=Alignment.Center){
        if(o.imageUrl!=null)SubcomposeAsyncImage(model=o.imageUrl,contentDescription=o.name,contentScale=ContentScale.Fit,modifier=Modifier.fillMaxSize().padding(10.dp),
            loading={Box(Modifier.fillMaxSize(),contentAlignment=Alignment.Center){CircularProgressIndicator(Modifier.size(24.dp),strokeWidth=2.dp)}},
            error={PhotoFallback(o,l,true)})
        else PhotoFallback(o,l,false)
    }
}
@Composable private fun PhotoFallback(o:Offer,l:String,failed:Boolean){
    Column(Modifier.fillMaxSize().padding(12.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){
        Icon(categoryIcon(o.category),null,Modifier.size(38.dp),tint=Color(0xFF707070))
        Spacer(Modifier.height(8.dp));Text(tr(l,if(failed)"image_failed" else "no_photo"),style=MaterialTheme.typography.labelSmall,color=Color(0xFF707070))
    }
}

@Composable fun ProductTile(o:Offer,favorite:Boolean,l:String,country:String,open:()->Unit,toggle:()->Unit){
    Card(onClick=open,shape=RoundedCornerShape(22.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface),elevation=CardDefaults.cardElevation(defaultElevation=1.dp),modifier=Modifier.fillMaxWidth()){
        Box {
            ProductPhoto(o,l,180)
            Surface(onClick=toggle,shape=CircleShape,color=MaterialTheme.colorScheme.surface.copy(alpha=0.95f),modifier=Modifier.align(Alignment.TopEnd).padding(8.dp)){
                Icon(if(favorite)Icons.Outlined.Favorite else Icons.Outlined.FavoriteBorder,tr(l,"favorites"),Modifier.padding(11.dp).size(20.dp),tint=MaterialTheme.colorScheme.primary)
            }
        }
        Column(Modifier.padding(14.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
            Text(o.platform.uppercase(Locale.getDefault()),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.primary,maxLines=1,overflow=TextOverflow.Ellipsis)
            Text(o.name,modifier=Modifier.heightIn(min=58.dp),style=MaterialTheme.typography.titleSmall,fontWeight=FontWeight.SemiBold,maxLines=3,overflow=TextOverflow.Ellipsis)
            Text(money(o.promoPrice,o.currency),style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.primary)
            Text(tr(l,o.kind),style=MaterialTheme.typography.labelSmall,maxLines=2)
            StatusPill(o.status,l)
            if(country=="pickup")Text(tr(l,"pickup"),style=MaterialTheme.typography.bodySmall)
            else (if(country=="both")listOf("ES","AD") else listOf(if(country=="AD")"AD" else "ES")).forEach{destination->
                val shipping=if(destination=="AD")o.shippingCostAd else o.shippingCostEs
                val status=if(destination=="AD")o.shippingAd else o.shippingEs
                Text("$destination · "+tr(l,status)+(shipping?.let{" · "+money(it,o.currency)}?:""),style=MaterialTheme.typography.bodySmall,maxLines=3)
            }
            if(o.imageCredit!=null)TextButton(onClick=open,contentPadding=PaddingValues(0.dp)){Icon(Icons.Outlined.Copyright,null,Modifier.size(14.dp));Spacer(Modifier.width(4.dp));Text(tr(l,"photo_credits"),style=MaterialTheme.typography.labelSmall)}
            if(o.additionalChargesEs!=null||o.additionalChargesAd!=null)Text(tr(l,"additional_costs"),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.error)
            if(o.sourceStatus in listOf("missing","unreachable")) Text(tr(l,"stale_source"),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.error)
            Text(readableDate(o.checkedAt),style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            Text(tr(l,"see_details"),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
        }
    }
}

@Composable fun SourcesScreen(sources:List<Source>,l:String){
    var query by remember{mutableStateOf("")}
    var onlyAutomatic by remember{mutableStateOf(false)}
    val context=LocalContext.current
    val shown=sources.filter{(query.isBlank()||it.name.contains(query,true))&&(!onlyAutomatic||it.enabled&&it.mode=="automated")}
    androidx.compose.foundation.lazy.LazyColumn(contentPadding=PaddingValues(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{Text(tr(l,"sources_title"),style=MaterialTheme.typography.headlineSmall,fontWeight=FontWeight.Bold);Spacer(Modifier.height(8.dp));Text(tr(l,"sources_note"),style=MaterialTheme.typography.bodyMedium)}
        item{OutlinedTextField(query,{query=it},placeholder={Text(tr(l,"search_sources"))},leadingIcon={Icon(Icons.Outlined.Search,null)},singleLine=true,shape=RoundedCornerShape(18.dp),modifier=Modifier.fillMaxWidth())
            FilterChip(onlyAutomatic,{onlyAutomatic=!onlyAutomatic},label={Text(tr(l,"automatic_only"))})}
        if(sources.isEmpty())item{Text(tr(l,"sources_empty"))}
        items(shown.size,key={shown[it].id}){index->val source=shown[index]
            Card(shape=RoundedCornerShape(22.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface)){
                Column(Modifier.fillMaxWidth().padding(18.dp),verticalArrangement=Arrangement.spacedBy(9.dp)){
                    Row(verticalAlignment=Alignment.CenterVertically){Icon(if(source.enabled)Icons.Outlined.RssFeed else Icons.Outlined.Language,null,tint=MaterialTheme.colorScheme.primary);Spacer(Modifier.width(10.dp));Text(source.name,style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)}
                    StatusPill(if(source.enabled&&source.mode=="automated")"source_automatic" else if(!source.enabled&&source.mode=="automated")"source_disabled" else "source_"+source.mode,l)
                    Text(source.policyNote.ifBlank{source.notes},style=MaterialTheme.typography.bodySmall)
                    if(source.url.isNotBlank())TextButton(onClick={runCatching{val uri=Uri.parse(source.url);if(uri.scheme=="https")context.startActivity(Intent(Intent.ACTION_VIEW,uri))}}){Text(tr(l,"visit_source"));Spacer(Modifier.width(6.dp));Icon(Icons.Outlined.OpenInNew,null,Modifier.size(16.dp))}
                }
            }
        }
    }
}
