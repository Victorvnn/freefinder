package org.freefinder.app

import com.google.gson.annotations.SerializedName

data class Evidence(val field:String="", val source:String="", @SerializedName("checked_at") val checkedAt:String="", val method:String="", val note:String="")
data class Offer(
    val id:String, @SerializedName("source_status") val sourceStatus:String?=null, val name:String, val description:String="", val brand:String?=null,
    val category:String="other", val platform:String="", val url:String,
    @SerializedName("image_url") val imageUrl:String?=null,
    @SerializedName("request_url") val requestUrl:String?=null,
    @SerializedName("image_credit") val imageCredit:String?=null,
    @SerializedName("image_license") val imageLicense:String?=null,
    @SerializedName("image_license_url") val imageLicenseUrl:String?=null,
    @SerializedName("regular_price") val regularPrice:Double?=null,
    @SerializedName("promo_price") val promoPrice:Double?=null,
    val currency:String="EUR", val kind:String="promotion",
    @SerializedName("shipping_es") val shippingEs:String="unknown",
    @SerializedName("shipping_ad") val shippingAd:String="unknown",
    @SerializedName("shipping_cost_es") val shippingCostEs:Double?=null,
    @SerializedName("shipping_cost_ad") val shippingCostAd:Double?=null,
    @SerializedName("additional_charges_es") val additionalChargesEs:Double?=null,
    @SerializedName("additional_charges_ad") val additionalChargesAd:Double?=null,
    @SerializedName("total_es") val totalEs:Double?=null,
    @SerializedName("total_ad") val totalAd:Double?=null,
    val requirements:List<String> = emptyList(), val residency:String?=null,
    @SerializedName("discovered_at") val discoveredAt:String="",
    @SerializedName("checked_at") val checkedAt:String="",
    @SerializedName("ends_at") val endsAt:String?=null,
    val status:String="pending", val keepable:Boolean?=null,
    @SerializedName("purchase_required") val purchaseRequired:Boolean?=null,
    val cachedOnly:Boolean=false, val confidence:Double=0.0, val evidence:List<Evidence> = emptyList(),
    @SerializedName("risk_reasons") val riskReasons:List<String> = emptyList()
)
data class Page(val items:List<Offer>,val total:Int)
data class SyncRun(val id:Int,val source:String,@SerializedName("started_at") val startedAt:String,@SerializedName("finished_at") val finishedAt:String?,val status:String,val count:Int,val error:String?)
data class Filters(val query:String="",val category:String="",val country:String="",val kind:String="",val maxShipping:Double?=null,val keepOnly:Boolean=false,val sort:String="newest",val brand:String="",val platform:String="",val status:String="",val includeUnknown:Boolean=false) {
    fun matches(o:Offer):Boolean = (query.isBlank() || "${o.name} ${o.brand.orEmpty()} ${o.platform}".contains(query,true)) &&
        (brand.isBlank()||o.brand==brand) && (platform.isBlank()||o.platform==platform) && (status.isBlank()||o.status==status) &&
        (category.isBlank()||o.category==category) && (kind.isBlank()||o.kind==kind) &&
        when(country){"ES"->(o.shippingEs=="confirmed"||(includeUnknown&&o.shippingEs=="unknown"));"AD"->(o.shippingAd=="confirmed"||(includeUnknown&&o.shippingAd=="unknown"));"both"->(o.shippingEs=="confirmed"||(includeUnknown&&o.shippingEs=="unknown"))&&(o.shippingAd=="confirmed"||(includeUnknown&&o.shippingAd=="unknown"));"pickup"->o.kind=="private_gift";else->true} &&
        (!keepOnly||o.keepable==true) && (o.purchaseRequired!=true) &&
        (maxShipping==null || (if(country=="both") listOf(o.shippingCostEs,o.shippingCostAd) else listOf(if(country=="AD") o.shippingCostAd else o.shippingCostEs)).all { it!=null && it<=maxShipping })
}
val categories=listOf("electronics","computing","appliances","home","tools","clothing","shoes","accessories","beauty","hygiene","food","pets","sport","automotive","office","garden","children","other")
val kinds=listOf("free_shipping","shipping_only","sample","keep_trial","selection","cashback","promotion","giveaway","private_gift","loan")

// Discovery directory entries are separate from Offer and never imply free stock.
data class Source(val id:String="",val name:String="",val url:String="",val mode:String="manual",val enabled:Boolean=false,
    val categories:List<String> = emptyList(),val notes:String="",
    @SerializedName("policy_note") val policyNote:String="",
    @SerializedName("policy_url") val policyUrl:String?=null)

/** Actual unit price zero, never a sample, lottery, cashback or returnable loan. */
fun Offer.matchesCatalog(mode:String):Boolean=when(mode){
    "zero"->promoPrice==0.0&&purchaseRequired==false&&kind !in listOf("sample","giveaway","cashback","loan","selection","keep_trial")
    "samples"->kind=="sample"
    "draws"->kind in listOf("giveaway","selection","keep_trial","cashback","loan")
    else->true
}
