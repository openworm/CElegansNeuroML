<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:meta="http://morphml.org/metadata/schema" 
    xmlns:cml="http://morphml.org/channelml/schema">

<!--

    This file is used to convert ChannelML files to NEURON mod files

    Funding for this work has been received from the Medical Research Council and the 
    Wellcome Trust. This file was initially developed as part of the neuroConstruct project
    
    Author: Padraig Gleeson
    Copyright 2009 University College London
    
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
-->

<xsl:output method="text" indent="yes" />

<xsl:variable name="xmlFileUnitSystem"><xsl:value-of select="/cml:channelml/@units"/></xsl:variable>   


<!-- Some parameters which can be changed to make more/less verbose output, etc.
     Some of these are changed in neuroConstruct before generating the script files-->

<xsl:variable name="debug">0</xsl:variable>  <!-- Comments printed during run e.g. when syn mechanism receives event-->

<xsl:variable name="favourPublicParameters">0</xsl:variable>  <!-- 0 or 1, make e.g. A, k, d of parameterised_hh accessible parameters in hoc-->

<xsl:variable name="forceCorrectInit">1</xsl:variable>  <!-- i.e. if 0 will ignore any initialisation elements in voltage_gate, and so set e.g. m = minf at t=0, as normal-->

<xsl:variable name="parallelMode">0</xsl:variable>  <!-- some mod files may be slightly different in parallel mode, e.g. gap junctions-->



<!--Main template-->

<xsl:template match="/cml:channelml">
?  This is a NEURON mod file generated from a ChannelML file

?  Unit system of original ChannelML file: <xsl:value-of select="$xmlFileUnitSystem"/><xsl:text>
</xsl:text>

<xsl:if test="count(/cml:channelml/cml:channel_type/cml:ks_gate) &gt; 0">
    *** Note: Kinetic scheme based ChannelML description cannot be mapped in to mod files in this version. ***
    Please use the alternative XSL file which maps on to NEURON's KS Channel Builder format 
    (should be ChannelML_v1.X.X_NEURONChanBuild.xsl)
    
</xsl:if>
<xsl:if test="count(meta:notes) &gt; 0">
COMMENT
    <xsl:value-of select="meta:notes"/>
ENDCOMMENT
</xsl:if>
<!-- Only do the first channel -->
<xsl:apply-templates  select="cml:channel_type"/>

<!-- Do the ion concentrations if there -->
<xsl:apply-templates  select="cml:ion_concentration"/>

<!-- Do a synapse if there -->
<xsl:apply-templates  select="cml:synapse_type"/>

</xsl:template>
<!--End Main template-->

<xsl:template match="cml:channel_type">
TITLE Channel: <xsl:value-of select="@name"/>

<xsl:if test="count(meta:notes) &gt; 0">

COMMENT
    <xsl:value-of select="meta:notes"/>
ENDCOMMENT
</xsl:if>

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (S) = (siemens)
    (um) = (micrometer)
    (molar) = (1/liter)
    (mM) = (millimolar)
    (l) = (liter)
}

<xsl:variable name="nonSpecificCurrent">
    <xsl:choose>
        <xsl:when test="cml:current_voltage_relation/cml:ohmic/@ion='non_specific'">yes</xsl:when>
        <xsl:when test="cml:current_voltage_relation/@ion='non_specific'">yes</xsl:when>
        <xsl:otherwise>no</xsl:otherwise>
    </xsl:choose>
</xsl:variable>
<!-- Whether there is a voltage and concentration depemnence in the channel-->
<xsl:variable name="voltConcDependence">
    <xsl:choose>
        <xsl:when test="count(//cml:voltage_conc_gate) &gt; 0">yes</xsl:when>
        <xsl:when test="count(//cml:conc_dependence) &gt; 0">yes</xsl:when>
        <xsl:otherwise>no</xsl:otherwise>
    </xsl:choose>
</xsl:variable>
    
NEURON {
<xsl:choose>
<xsl:when test="count(cml:current_voltage_relation/cml:ohmic) &gt; 0 or cml:current_voltage_relation[@cond_law='ohmic']">  <!-- i.e. normal ohmic channel-->
    SUFFIX <xsl:value-of select="@name"/>
    
    <xsl:for-each select="/cml:channelml/cml:ion[@name!='non_specific']">
        <xsl:choose>
            <xsl:when test ="@role='PermeatedSubstanceFixedRevPot'">
    USEION <xsl:value-of select="@name"/> WRITE i<xsl:value-of select="@name"/> VALENCE <xsl:value-of select="@charge"/> ? reversal potential of ion is **NOT READ**, outgoing current is written
            </xsl:when>
            <xsl:when test ="@role='ModulatingSubstance'">
    USEION <xsl:value-of select="@name"/> READ <xsl:value-of select="@name"/>i VALENCE <xsl:value-of select="@charge"/> ? internal concentration of ion is read
            </xsl:when>
            <xsl:when test ="@role='SignallingSubstance'">
    USEION <xsl:value-of select="@name"/> READ i<xsl:value-of select="@name"/> WRITE <xsl:value-of select="@name"/>i VALENCE <xsl:value-of select="@charge"/> ? outgoing current of ion is read, internal concentration is written
            </xsl:when>
            <xsl:otherwise>
    USEION <xsl:value-of select="@name"/> READ e<xsl:value-of select="@name"/> WRITE i<xsl:value-of select="@name"/> VALENCE <xsl:value-of select="@charge"/> ? reversal potential of ion is read, outgoing current is written
            </xsl:otherwise>
        </xsl:choose>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/@ion">
        <xsl:if test="string($nonSpecificCurrent)='no'">
            <xsl:variable name="charge"><xsl:choose><xsl:when test="count(../@charge) &gt; 0"> VALENCE <xsl:value-of select="../@charge"></xsl:value-of></xsl:when>
            <xsl:otherwise> VALENCE 1 </xsl:otherwise></xsl:choose></xsl:variable>
    USEION <xsl:value-of select="."/> <xsl:if test="count(../@fixed_erev) = 0 or string(../@fixed_erev)='no'"> READ e<xsl:value-of select="."/> </xsl:if> WRITE i<xsl:value-of select="."/> <xsl:value-of select="$charge"/> ? <xsl:if test="count(../@fixed_erev) = 0 or string(../@fixed_erev)='no'">reversal potential of ion is read,</xsl:if> outgoing current is written
           
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:conc_dependence">
        <xsl:variable name="charge"><xsl:choose><xsl:when test="count(@charge) &gt; 0"> VALENCE <xsl:value-of select="@charge"></xsl:value-of></xsl:when>
            <xsl:otherwise> VALENCE 1 </xsl:otherwise></xsl:choose></xsl:variable>
    USEION <xsl:value-of select="@ion"/> READ <xsl:value-of select="@ion"/>i<xsl:value-of select="$charge"/> ? internal concentration of ion is read

    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:conc_factor">
        <xsl:variable name="charge"><xsl:choose><xsl:when test="count(@charge) &gt; 0"> VALENCE <xsl:value-of select="@charge"></xsl:value-of></xsl:when>
            <xsl:otherwise> VALENCE 1 </xsl:otherwise></xsl:choose></xsl:variable>
    USEION <xsl:value-of select="@ion"/> READ <xsl:value-of select="@ion"/>i<xsl:value-of select="$charge"/> ? internal concentration of ion is read

    </xsl:for-each>
    
    
    <xsl:if test="string($nonSpecificCurrent)='yes'">
    ? A non specific current is present
    RANGE e
    NONSPECIFIC_CURRENT i
    </xsl:if>
    RANGE gmax, gion
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
        <xsl:variable name="state"><xsl:value-of select="cml:state/@name"/></xsl:variable>
    RANGE <xsl:value-of select="$state"/>inf, <xsl:value-of select="$state"/>tau<xsl:if test="$favourPublicParameters = 1">
    <xsl:for-each select="../../../../cml:hh_gate[@state=$state]/cml:transition/cml:voltage_gate/*/cml:parameterised_hh">
        <xsl:for-each select="cml:parameter">, <xsl:value-of select="@name"/>_<xsl:value-of select="name(../..)"/>_<xsl:value-of select="$state"/>
        </xsl:for-each>
    </xsl:for-each></xsl:if>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state">
        <xsl:variable name="gateName"><xsl:value-of select="@id"/></xsl:variable>
    RANGE <xsl:value-of select="$gateName"/>inf, <xsl:value-of select="$gateName"/>tau
    </xsl:for-each>

    <xsl:for-each select="cml:current_voltage_relation/cml:gate">
        <xsl:if test="count(cml:closed_state) &gt; 1">
            <xsl:for-each select="cml:transition">RANGE <xsl:value-of select="@name"/> <xsl:text>
    </xsl:text>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>


    <xsl:for-each select="cml:parameters/cml:parameter">
    RANGE <xsl:value-of select="@name"/>
    </xsl:for-each>
</xsl:when>
<xsl:when test="count(cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">  <!-- i.e. I&F-->
    ? Note this implementation is based on that used in the COBA based I and F model as used in Brette et al (2006)
    ? and the NEURON script files from http://senselab.med.yale.edu/SenseLab/ModelDB/ShowModel.asp?model=83319
    
    POINT_PROCESS <xsl:value-of select="@name"/>
    GLOBAL thresh, t_refrac, v_reset, g_refrac
    NONSPECIFIC_CURRENT i
</xsl:when>
</xsl:choose>
}

PARAMETER { 
<xsl:choose>
<xsl:when test="count(cml:current_voltage_relation/cml:ohmic)">  <!-- i.e. normal ohmic channel pre v1.7.3-->
    gmax = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/cml:ohmic/cml:conductance/@default_gmax"/>
            <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
          </xsl:call-template> (S/cm2) ? default value, should be overwritten when conductance placed on cell
    <xsl:if test="string($nonSpecificCurrent)='yes'">
    e = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="/cml:channelml/cml:ion[@name='non_specific']/@default_erev"/>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template> (mV) ? default value, should be overwritten when conductance placed on cell
    </xsl:if>
    <xsl:if test="$favourPublicParameters = 1">
    <xsl:for-each select="cml:hh_gate/cml:transition/cml:voltage_gate/*/cml:parameterised_hh">
        <xsl:for-each select="cml:parameter">
    <xsl:value-of select="@name"/>_<xsl:value-of select="name(../..)"/>_<xsl:value-of select="../../../../../@state"/> = <xsl:value-of select="@value"/><xsl:text>
    </xsl:text>
                
        </xsl:for-each>
    </xsl:for-each></xsl:if>
</xsl:when>
<xsl:when test="cml:current_voltage_relation[@cond_law='ohmic']">  <!-- i.e. normal ohmic channel from v1.7.3-->
    gmax = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/@default_gmax"/>
            <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
          </xsl:call-template> (S/cm2)  ? default value, should be overwritten when conductance placed on cell
    <xsl:if test="string($nonSpecificCurrent)='yes'">
    e = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/@default_erev"/>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template> (mV) ? default value, should be overwritten when conductance placed on cell
    </xsl:if>
</xsl:when>
<xsl:when test="count(cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">  <!-- i.e. I&F-->
    thresh = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/cml:integrate_and_fire/@threshold"/>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template> (mV)
    t_refrac = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/cml:integrate_and_fire/@t_refrac"/>
            <xsl:with-param name="quantity">Time</xsl:with-param>
            </xsl:call-template> (ms)
    v_reset = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/cml:integrate_and_fire/@v_reset"/>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template> (mV)
    g_refrac = <xsl:call-template name="convert">
            <xsl:with-param name="value" select="cml:current_voltage_relation/cml:integrate_and_fire/@g_refrac"/>
            <xsl:with-param name="quantity">Conductance</xsl:with-param>
            </xsl:call-template> (uS)
</xsl:when>
</xsl:choose>
<xsl:for-each select="cml:parameters/cml:parameter"><xsl:text>
    </xsl:text><xsl:value-of select="@name"/> = <xsl:value-of select="@value"/> : Note units of this will be determined by its usage in the generic functions
</xsl:for-each>
}



ASSIGNED {
<xsl:choose>
<xsl:when test="count(cml:current_voltage_relation/cml:ohmic) &gt; 0 or cml:current_voltage_relation[@cond_law='ohmic']">  <!-- i.e. normal ohmic channel-->
    v (mV)
    <xsl:choose>
        <xsl:when test="string($nonSpecificCurrent)='yes'">    
    i (mA/cm2)
        </xsl:when>
        <xsl:otherwise>
    celsius (degC)
    <xsl:for-each select="/cml:channelml/cml:ion[@name!='non_specific']">
        <xsl:choose>
            <xsl:when test ="@role='ModulatingSubstance'">
    ? The internal concentration of ion: <xsl:value-of select="@name"/> is used in the rate equations...
    <xsl:value-of select="@name"/>i (mM)           
            </xsl:when>
            <xsl:when test ="@role='SignallingSubstance'">
            ? Error!! ion: <xsl:value-of select="@name"/> with role="SignallingSubstance" shouldn't be in a channel_type...
            </xsl:when>
            <xsl:otherwise>
    ? Reversal potential of <xsl:value-of select="@name"/>
    e<xsl:value-of select="@name"/> (mV)
    ? The outward flow of ion: <xsl:value-of select="@name"/> calculated by rate equations...
    i<xsl:value-of select="@name"/> (mA/cm2)
            </xsl:otherwise>
        </xsl:choose>
    </xsl:for-each>
    
    <xsl:for-each select="cml:current_voltage_relation/@ion">  <!-- post v1.7.3 -->
    ? Reversal potential of <xsl:value-of select="."/>
    e<xsl:value-of select="."/> (mV)
    ? The outward flow of ion: <xsl:value-of select="."/> calculated by rate equations...
    i<xsl:value-of select="."/> (mA/cm2)
    </xsl:for-each>
    
    <xsl:for-each select="cml:current_voltage_relation/cml:conc_dependence">  <!-- post v1.7.3 -->
    ? The internal concentration of ion: <xsl:value-of select="@ion"/> is used in the rate equations...
    <xsl:value-of select="@ion"/>i (mM)   
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:conc_factor">  <!-- post v1.7.3 -->
    ? The internal concentration of ion: <xsl:value-of select="@ion"/> is used in the rate equations...
    <xsl:value-of select="@ion"/>i (mM)   
    </xsl:for-each>
    
    gion (S/cm2)
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
        <xsl:value-of select="cml:state/@name"/>inf<xsl:text>
    </xsl:text><xsl:value-of select="cml:state/@name"/>tau (ms)<xsl:text>
    </xsl:text></xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state">
        <xsl:value-of select="@id"/>inf<xsl:text>
    </xsl:text><xsl:value-of select="@id"/>tau (ms)<xsl:text>
    </xsl:text></xsl:for-each>

    <xsl:for-each select="cml:current_voltage_relation/cml:gate">
        <xsl:if test="count(cml:closed_state) &gt; 1">
            <xsl:for-each select="cml:transition"><xsl:value-of select="@name"/> (/ms)<xsl:text>
    </xsl:text>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
        </xsl:otherwise>
    </xsl:choose>
</xsl:when>
<xsl:when test="count(cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">  <!-- i.e. I&F-->
    i (nanoamp)
    v (millivolt)
    g (microsiemens)

</xsl:when>
</xsl:choose>
}

BREAKPOINT { <xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:conc_factor) &gt; 0">LOCAL g_factor, <xsl:value-of 
select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:conc_factor/@variable_name"/><xsl:text>
    
</xsl:text>
</xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:conc_factor) &gt; 0">LOCAL g_factor, <xsl:value-of 
select="cml:current_voltage_relation/cml:conc_factor/@variable_name"/><xsl:text>
    
</xsl:text>
</xsl:if>

<xsl:choose>
<xsl:when test="count(cml:current_voltage_relation/cml:ohmic) &gt; 0 or cml:current_voltage_relation[@cond_law='ohmic']">  <!-- i.e. normal ohmic channel-->
    <xsl:choose>
        <xsl:when test="string($nonSpecificCurrent)='yes'">
    i = gmax*(v - e) 
        </xsl:when>
        <xsl:otherwise>
    <xsl:choose>
        <xsl:when test="count(cml:current_voltage_relation/cml:gate) = 1 and count(cml:current_voltage_relation/cml:gate/cml:closed_state) &gt; 1">

    SOLVE kin METHOD sparse
        </xsl:when>
        <xsl:when test="$voltConcDependence='yes'">
    SOLVE states METHOD derivimplicit</xsl:when> <!-- Needed for concentration dependence-->
    
        <xsl:when test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate) &gt; 0 or
                    count(cml:current_voltage_relation/cml:gate) &gt; 0">
                        
    SOLVE states METHOD cnexp
        </xsl:when> <!-- When it's not a nonSpecificCurrent but there are no gates, this statement is not needed-->
    </xsl:choose>
    <xsl:if test="count(cml:current_voltage_relation/cml:ohmic) &gt; 0"> <!-- pre v1.7.3 -->
    gion = gmax<xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">*((<xsl:if test="count(cml:state/@fraction) &gt; 0">
            <xsl:value-of select="cml:state/@fraction"/>*</xsl:if><xsl:value-of select="cml:state/@name"/>)^<xsl:value-of select="@power"/>)</xsl:for-each>
    </xsl:if>
    <xsl:if test="count(cml:current_voltage_relation/cml:gate) &gt; 0"> <!-- post v1.7.3 -->
        <xsl:for-each select="cml:current_voltage_relation/cml:gate">
    </xsl:for-each>
    gion = gmax<xsl:for-each select="cml:current_voltage_relation/cml:gate"> * (<xsl:if test="count(cml:open_state) &gt; 1">( </xsl:if> <xsl:for-each select="cml:open_state"><xsl:if test="position() &gt; 1"> + </xsl:if> <xsl:if test="count(@fraction) &gt; 0">(<xsl:value-of select="@fraction"/>*</xsl:if><xsl:value-of select="@id"/><xsl:if test="count(@fraction) &gt; 0">)</xsl:if> </xsl:for-each><xsl:if test="count(cml:open_state) &gt; 1"> )</xsl:if>^<xsl:value-of select="@instances"/>)</xsl:for-each>
    </xsl:if>
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:conc_factor | cml:current_voltage_relation/cml:conc_factor">
    <xsl:text>
        
    </xsl:text><xsl:value-of select="@variable_name"/> = <xsl:value-of select="@ion"/>i / <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Concentration</xsl:with-param>
                    </xsl:call-template>   
    <xsl:call-template name="formatExpression">
        <xsl:with-param name="variable">g_factor</xsl:with-param>
        <xsl:with-param name="oldExpression">
            <xsl:value-of select="@expr" />
        </xsl:with-param>
    </xsl:call-template>
    
    gion = gion * g_factor
    </xsl:for-each>
    
            <xsl:for-each select="/cml:channelml/cml:ion">  <!-- pre v1.7.3 -->
                <xsl:if test ="count(@role) = 0 or @role='PermeatedSubstance' or @role='PermeatedSubstanceFixedRevPot'">
    i<xsl:value-of select="@name"/> = gion*(v - e<xsl:value-of select="@name"/>)
                </xsl:if>
            </xsl:for-each>
            <xsl:for-each select="cml:current_voltage_relation/@ion">  <!-- post v1.7.3 -->
    i<xsl:value-of select="."/> = gion*(v - e<xsl:value-of select="."/>)
            </xsl:for-each>
        </xsl:otherwise>
        </xsl:choose>
</xsl:when>
<xsl:when test="count(cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">  <!-- i.e. I&F-->
    i = g*(v - v_reset)
</xsl:when>
</xsl:choose>

}


<xsl:if test="count(cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">

INITIAL {
    net_send(0, 3)
    g = 0
}

NET_RECEIVE(w) {

    if (flag == 1) {
        v = v_reset
        g = g_refrac
        <xsl:if test="$debug = 1">
        printf("+++++++ Spiking cell at: %g, v: %g\n", t, v)
        </xsl:if>
        net_event(t)
        net_send(t_refrac, 2)
    }else if (flag == 2) {
        g = 0
        <xsl:if test="$debug = 1">
        printf("+++++++ Finished refract at: %g, v: %g\n", t, v)
        </xsl:if>
    }else if (flag == 3) {
        WATCH (v > thresh) 1
    }	
}   
</xsl:if>
    
<xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate) &gt; 0 or
              count(cml:current_voltage_relation/cml:gate) &gt; 0">
INITIAL {
    <xsl:variable name="ionname"><xsl:value-of select="cml:current_voltage_relation/cml:ohmic/@ion"/><xsl:value-of select="cml:current_voltage_relation/@ion"/></xsl:variable>  <!-- one or the other present-->
    <xsl:variable name="defaultErev"><xsl:call-template name="convert">
        <xsl:with-param name="value"><xsl:value-of select="/cml:channelml/cml:ion[@name=$ionname]/@default_erev"/><xsl:value-of select="cml:current_voltage_relation/@default_erev"/></xsl:with-param> <!-- one or the other present-->
        <xsl:with-param name="quantity">Voltage</xsl:with-param>
        </xsl:call-template>
    </xsl:variable>
    <xsl:for-each select="/cml:channelml/cml:ion">
    <xsl:if test ="count(@role) = 0 or @role='PermeatedSubstance' or @role='PermeatedSubstanceFixedRevPot'">e<xsl:value-of select="@name"/> = <xsl:value-of select="$defaultErev"/><xsl:text>
        </xsl:text>
            </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/@ion">
    e<xsl:value-of select="."/> = <xsl:value-of select="$defaultErev"/><xsl:text>
        </xsl:text>
    </xsl:for-each>
        
        <xsl:choose>
            <xsl:when test="$voltConcDependence='yes'">
    settables(v,cai)
    </xsl:when>
            <xsl:otherwise>
    rates(v)
    </xsl:otherwise>
        </xsl:choose>
    
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
    <xsl:variable name="stateName" select="cml:state/@name"/>
    <xsl:value-of select="$stateName"/> = <xsl:value-of select="$stateName"/>inf
        <xsl:if test="$forceCorrectInit='0' and count(../../../../cml:hh_gate[@state=$stateName]/cml:transition/cml:voltage_gate/cml:initialisation) &gt; 0">
            <xsl:value-of select="$stateName"/> = <xsl:value-of select="../../../../cml:hh_gate[@state=$stateName]/cml:transition/cml:voltage_gate/cml:initialisation/@value"/>: Hard coded initialisation!!
        </xsl:if>        
        <xsl:if test="$forceCorrectInit='0' and count(../../../../cml:hh_gate[@state=$stateName]/cml:transition/cml:voltage_conc_gate/cml:initialisation) &gt; 0">
            <xsl:value-of select="$stateName"/> = <xsl:value-of select="../../../../cml:hh_gate[@state=$stateName]/cml:transition/cml:voltage_conc_gate/cml:initialisation/@value"/>: Hard coded initialisation!!
        </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="cml:current_voltage_relation/cml:gate">
    <xsl:choose>
    <xsl:when test="count(cml:closed_state) = 1">
    <xsl:for-each select="cml:open_state">
    <xsl:variable name="stateName" select="@id"/>
    <xsl:value-of select="$stateName"/> = <xsl:value-of select="$stateName"/>inf
        <xsl:if test="$forceCorrectInit='0' and count(../cml:initialisation) &gt; 0">
            <xsl:value-of select="$stateName"/> = <xsl:value-of select="../cml:initialisation/@value"/>: Hard coded initialisation!!
        </xsl:if></xsl:for-each></xsl:when>
    <xsl:otherwise>SOLVE kin STEADYSTATE sparse</xsl:otherwise>
    </xsl:choose>
    </xsl:for-each>
    
}
    
STATE {
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
    <xsl:value-of select="cml:state/@name"/><xsl:text>
    </xsl:text>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate">
        <xsl:if test="count(cml:closed_state) &gt; 1">
            <xsl:for-each select="cml:closed_state">
    <xsl:value-of select="@id"/><xsl:text>
    </xsl:text>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state">
    <xsl:value-of select="@id"/><xsl:text>
    </xsl:text>
    </xsl:for-each>
}

<xsl:choose>
    <xsl:when test="count(cml:current_voltage_relation/cml:gate[1]/cml:closed_state) &gt; 1">

KINETIC kin {
    <xsl:choose>
        <xsl:when test="$voltConcDependence='yes'">settables(v,cai)
    </xsl:when>
        <xsl:otherwise>rates(v)
    </xsl:otherwise>
    </xsl:choose>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:transition">
        <xsl:variable name="from"><xsl:value-of select="@from"/></xsl:variable>
        <xsl:variable name="to"><xsl:value-of select="@to"/></xsl:variable>
        <xsl:variable name="position"><xsl:value-of select="position()"/></xsl:variable>
        <xsl:variable name="positionRev"><xsl:for-each select="../cml:transition"><xsl:if test="@from=$to"><xsl:if test="@to=$from"><xsl:value-of select="position()"/></xsl:if></xsl:if></xsl:for-each></xsl:variable>
       
    <!--<xsl:choose>
    <xsl:when test="../cml:transition[@to=$from
    ..<xsl:value-of select="number($position)"/>..
    <xsl:value-of select="$positionRev"/>
    ++<xsl:value-of select="number($positionRev)"/>++-->
    
        <xsl:if test="number($position) &lt; number($positionRev)">
    ~ <xsl:value-of select="$from"/> &lt;-> <xsl:value-of select="$to"/> (<xsl:value-of select="@name"/>, <xsl:value-of select="../cml:transition[number($positionRev)]/@name"/>) </xsl:if>
    </xsl:for-each>
    CONSERVE <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:closed_state | cml:current_voltage_relation/cml:gate/cml:open_state"><xsl:if test="position() > 1"> + </xsl:if><xsl:value-of select="@id"/></xsl:for-each> = 1
}

</xsl:when>
    <xsl:otherwise>

DERIVATIVE states {
    <xsl:choose>
        <xsl:when test="$voltConcDependence='yes'">settables(v,cai)
    </xsl:when>
        <xsl:otherwise>rates(v)
    </xsl:otherwise>
    </xsl:choose>
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
    <xsl:value-of select="cml:state/@name"/>' = (<xsl:value-of select="cml:state/@name"/>inf - <xsl:value-of select="cml:state/@name"/>)/<xsl:value-of select="cml:state/@name"/>tau<xsl:text>
    </xsl:text></xsl:for-each>

    <xsl:choose>
        <xsl:when test="count(cml:current_voltage_relation/cml:gate/cml:closed_state) = count(cml:current_voltage_relation/cml:gate)">
            <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state">
            <xsl:value-of select="@id"/>' = (<xsl:value-of select="@id"/>inf - <xsl:value-of select="@id"/>)/<xsl:value-of select="@id"/>tau<xsl:text>
            </xsl:text></xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
            <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:closed_state | cml:current_voltage_relation/cml:gate/cml:open_state">
                <xsl:variable name="id"><xsl:value-of select="@id"/></xsl:variable>
                <xsl:value-of select="$id"/>' = 0 <xsl:for-each select="../cml:transition[@to=$id]"> + <xsl:value-of select="@name"/> * (1 - <xsl:value-of select="$id"/>)</xsl:for-each>
                <xsl:for-each select="../cml:transition[@from=$id]"> - <xsl:value-of select="@name"/> * <xsl:value-of select="$id"/>
                    </xsl:for-each><xsl:text> 
    </xsl:text> 
            </xsl:for-each>
        </xsl:otherwise>
    </xsl:choose>

}

</xsl:otherwise>
</xsl:choose>


<xsl:choose>
    <xsl:when test="$voltConcDependence='yes'">PROCEDURE settables(v(mV), cai(mM)) { </xsl:when>
    <xsl:otherwise>PROCEDURE rates(v(mV)) { </xsl:otherwise>
    </xsl:choose> 
    
    ? Note: not all of these may be used, depending on the form of rate equations
    LOCAL  alpha, beta, tau, inf, gamma, zeta<xsl:for-each select='cml:hh_gate/cml:transition/cml:voltage_conc_gate/cml:conc_dependence'
    >, <xsl:value-of select="@variable_name"/>
        </xsl:for-each><xsl:for-each select='cml:current_voltage_relation/cml:conc_dependence'
    >, <xsl:value-of select="@variable_name"/> </xsl:for-each> <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">
        <xsl:variable name="stateName"><xsl:value-of select="cml:state/@name"/></xsl:variable>, temp_adj_<xsl:value-of select="$stateName"/><xsl:for-each select='../../../../cml:hh_gate[@state=$stateName]/cml:transition/*/*'
        ><xsl:if  test="name()!='conc_dependence' and name()!='initialisation'"
            ><xsl:if test="$favourPublicParameters = 0">, A_<xsl:value-of select="name()"/>_<xsl:value-of select="$stateName"/>, k_<xsl:value-of select="name()"/>_<xsl:value-of  
            select="$stateName"/>, d_<xsl:value-of select="name()"/>_<xsl:value-of select="$stateName"/></xsl:if></xsl:if>
    </xsl:for-each>
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate"
    ><xsl:variable name="gateName"><xsl:value-of select="@name"/></xsl:variable>, temp_adj_<xsl:value-of select="$gateName"/>
        <xsl:for-each select='cml:transition | cml:time_course | cml:steady_state'
        ><xsl:variable name="stateName"><xsl:value-of select="@id"/></xsl:variable><xsl:if test="$favourPublicParameters = 0">,<xsl:text>
        </xsl:text> A_<xsl:value-of select="@name"/>_<xsl:value-of select="$gateName"/>, B_<xsl:value-of select="@name"/>_<xsl:value-of
            select="$gateName"/>, Vhalf_<xsl:value-of select="@name"/>_<xsl:value-of select="$gateName"/>  </xsl:if>
    </xsl:for-each>
    
    
    </xsl:for-each>
    
    
    <xsl:variable name="numGates"><xsl:value-of select="count(cml:hh_gate) + count(cml:current_voltage_relation/cml:gate)"/></xsl:variable>
    
    <xsl:if test="$voltConcDependence='no'">
        
        <xsl:variable name="max_v">
            <xsl:choose>
                <xsl:when test="count(cml:impl_prefs/cml:table_settings) = 0">100</xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="convert">
                        <xsl:with-param name="value"><xsl:value-of select="cml:impl_prefs/cml:table_settings/@max_v"/></xsl:with-param>
                        <xsl:with-param name="quantity">Voltage</xsl:with-param>
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>     
        
        <xsl:variable name="min_v">
            <xsl:choose>
                <xsl:when test="count(cml:impl_prefs/cml:table_settings) = 0">-100</xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="convert">
                        <xsl:with-param name="value"><xsl:value-of select="cml:impl_prefs/cml:table_settings/@min_v"/></xsl:with-param>
                        <xsl:with-param name="quantity">Voltage</xsl:with-param>
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>       
        </xsl:variable>
        
        <xsl:variable name="table_divisions">
            <xsl:choose>
                <xsl:when test="count(cml:impl_prefs/cml:table_settings) = 0">400</xsl:when>
                <xsl:otherwise><xsl:value-of select="cml:impl_prefs/cml:table_settings/@table_divisions"/></xsl:otherwise>
            </xsl:choose>
        </xsl:variable>

    <xsl:if test="count(cml:current_voltage_relation/cml:gate/cml:closed_state) = count(cml:current_voltage_relation/cml:gate)">
    TABLE <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate"><xsl:value-of 
    select="cml:state/@name"/>inf, <xsl:value-of select="cml:state/@name"/>tau<xsl:if test="position() &lt; number($numGates)">,</xsl:if> 
    </xsl:for-each><xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state"><xsl:value-of 
    select="@id"/>inf, <xsl:value-of select="@id"/>tau<xsl:if test="position() &lt; number($numGates)">,</xsl:if> 
    </xsl:for-each> DEPEND celsius<xsl:for-each select="cml:parameters/cml:parameter">, <xsl:value-of select="@name"/></xsl:for-each><xsl:if test="$favourPublicParameters = 1">
    <xsl:for-each select="cml:hh_gate/cml:transition/cml:voltage_gate/*/cml:parameterised_hh">
        <xsl:for-each select="cml:parameter">, <xsl:value-of select="@name"/>_<xsl:value-of select="name(../..)"/>_<xsl:value-of select="../../../../../@state"/></xsl:for-each>
    </xsl:for-each></xsl:if> FROM <xsl:value-of select="$min_v"/> TO <xsl:value-of select="$max_v"/> WITH <xsl:value-of select="$table_divisions"/></xsl:if>
    </xsl:if>
    
    UNITSOFF
    <xsl:choose>
        <xsl:when test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:q10_settings) &gt; 0 or
                        count(cml:current_voltage_relation/cml:q10_settings) &gt; 0">
    ? There is a Q10 factor which will alter the tau of the gates 
            <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:q10_settings |
                                  cml:current_voltage_relation/cml:q10_settings">
                <xsl:choose>
                    <xsl:when test="count(@gate) &gt; 0">
                        <xsl:choose><xsl:when test="count(@q10_factor) &gt; 0">
    temp_adj_<xsl:value-of select="@gate"/> = <xsl:value-of select="@q10_factor" />^((celsius - <xsl:value-of select="@experimental_temp"/>)/10)
                        </xsl:when><xsl:when test="count(@fixed_q10) &gt; 0">
    temp_adj_<xsl:value-of select="@gate"/> = <xsl:value-of select="@fixed_q10" />
                        </xsl:when></xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:choose><xsl:when test="count(@q10_factor) &gt; 0">
                            <xsl:variable name="expression"><xsl:value-of select="@q10_factor" />^((celsius - <xsl:value-of select="@experimental_temp"/>)/10)</xsl:variable>
                            <xsl:for-each select="../../cml:gate"> <!-- pre v1.7.3 -->
    temp_adj_<xsl:value-of select="cml:state/@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                            <xsl:for-each select="../cml:gate"> <!-- post v1.7.3 -->
    temp_adj_<xsl:value-of select="@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                        </xsl:when><xsl:when test="count(@fixed_q10) &gt; 0">     
                            <xsl:variable name="expression"><xsl:value-of select="@fixed_q10" /></xsl:variable>
                            <xsl:for-each select="../../cml:gate">
    temp_adj_<xsl:value-of select="cml:state/@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                            <xsl:for-each select="../cml:gate/cml:open_state">
    temp_adj_<xsl:value-of select="@id"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                        </xsl:when></xsl:choose>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">temp_adj_<xsl:value-of 
    select="cml:state/@name"/> = 1
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate/cml:open_state">temp_adj_<xsl:value-of 
    select="@id"/> = 1
    </xsl:for-each>
        </xsl:otherwise>
    </xsl:choose>
    
    <xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:offset) &gt; 0 or
                  count(cml:current_voltage_relation/cml:offset) &gt; 0">
        <xsl:variable name="offset"><xsl:value-of select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:offset/@value"/><xsl:value-of select="cml:current_voltage_relation/cml:offset/@value"/></xsl:variable>
    
    ? There is a voltage offset of <xsl:value-of select="$offset"/>. This will shift the dependency of the rate equations 
    v = v - (<xsl:call-template name="convert">
            <xsl:with-param name="value" select="$offset"/>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template>)<xsl:text>
    </xsl:text>          
    </xsl:if>
    
    
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">  <!-- pre v1.7.3 format -->
        
        <xsl:variable name="stateName" select="cml:state/@name"/>
            
        <xsl:for-each select='../../../../cml:hh_gate[@state=$stateName]'>
                
        <xsl:for-each select='cml:transition/cml:voltage_conc_gate/cml:conc_dependence'>
    ? Gate depends on the concentration of <xsl:value-of select="@ion"/><xsl:text>
    </xsl:text>   
    <xsl:value-of select="@variable_name"/> = <xsl:value-of select="@ion"/>i ? In NEURON, the variable for the concentration  of <xsl:value-of select="@ion"/> is <xsl:value-of select="@ion"/>i
    </xsl:for-each>
        
    ?      ***  Adding rate equations for gate: <xsl:value-of select="$stateName"/>  ***<xsl:text>
        </xsl:text>   
    <xsl:for-each select='cml:transition/cml:voltage_gate/* | 
                          cml:transition/cml:voltage_conc_gate/*'>
        
        <xsl:if  test="name()!='conc_dependence'">
            <xsl:choose>
                <xsl:when  test="count(cml:parameterised_hh) &gt; 0">
    ? Found a parameterised form of rate equation for <xsl:value-of select="name()"/>, using expression: <xsl:choose>
                                        <xsl:when test="cml:parameterised_hh/@type='linoid'" >A*(k*(v-d)) / (1 - exp(-(k*(v-d))))</xsl:when>
                                        <xsl:when test="cml:parameterised_hh/@type='exponential'" >A*exp(k*(v-d))</xsl:when>
                                        <xsl:when test="cml:parameterised_hh/@type='sigmoid'" >A / (1 + exp(k*(v-d)))</xsl:when>
                                        <xsl:otherwise >Unsupported expression type!</xsl:otherwise></xsl:choose><xsl:text>
    </xsl:text>   
    
    <xsl:variable name="A_name">A_<xsl:value-of select="name()"/>_<xsl:value-of select="$stateName"/></xsl:variable>
    <xsl:variable name="k_name">k_<xsl:value-of select="name()"/>_<xsl:value-of select="$stateName"/></xsl:variable>
    <xsl:variable name="d_name">d_<xsl:value-of select="name()"/>_<xsl:value-of select="$stateName"/></xsl:variable>
    
                    <xsl:for-each select="cml:parameterised_hh/cml:parameter">
                        <xsl:if test="$favourPublicParameters = 0">
    <xsl:value-of select="@name"/>_<xsl:value-of select="name(../..)"/>_<xsl:value-of select="$stateName"/> = <xsl:value-of select="@value"/><xsl:text>
    </xsl:text></xsl:if>
                    </xsl:for-each>
    
                    <xsl:if test="$xmlFileUnitSystem  = 'SI Units'">
    ? Unit system in ChannelML file is SI units, therefore need to 
    ? convert these to NEURON quanities...
                        <xsl:choose>
                            <xsl:when test="string(name()) = 'alpha' or string(name()) = 'beta'">
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/> * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">InvTime</xsl:with-param>
            </xsl:call-template>   ? 1/ms
    </xsl:when>
                            <xsl:when test="string(name()) = 'tau'">
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">Time</xsl:with-param>
        </xsl:call-template>   ? ms
    </xsl:when>
                            <xsl:when test="string(name()) = 'inf'">
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/>   ? Dimensionless
    </xsl:when>
                        </xsl:choose>
    <xsl:value-of select="$k_name"/> = <xsl:value-of select="$k_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
          </xsl:call-template>   ? mV
    <xsl:value-of select="$d_name"/> = <xsl:value-of select="$d_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
          </xsl:call-template>   ? mV
          
                    </xsl:if>
    <!--B = 1/<xsl:value-of select="$k_name"/>--><xsl:text> 
    
    </xsl:text>
                    <xsl:choose>
                        <xsl:when test="cml:parameterised_hh/@type='exponential'">
    <xsl:value-of select="name()"/> = <xsl:value-of select="$A_name"/> * exp((v - <xsl:value-of select="$d_name"/>) * <xsl:value-of select="$k_name"/>)<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                        <xsl:when test="cml:parameterised_hh/@type='sigmoid'">
    <xsl:value-of select="name()"/> = <xsl:value-of select="$A_name"/> / (exp((v - <xsl:value-of select="$d_name"/>) * <xsl:value-of select="$k_name"/>) + 1)<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                        <xsl:when test="cml:parameterised_hh/@type='linoid'">
    <xsl:value-of select="name()"/> = <xsl:value-of select="$A_name"/> * vtrap((v - <xsl:value-of select="$d_name"/>), (1/<xsl:value-of select="$k_name"/>))<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                    </xsl:choose>
    
    
                </xsl:when>
                <xsl:when test="count(cml:generic_equation_hh) &gt; 0 or count(cml:generic) &gt; 0">
                    <xsl:variable name="expr"><xsl:value-of select="cml:generic_equation_hh/@expr" /><xsl:value-of select="cml:generic/@expr" /></xsl:variable> <!--Will be one or the other-->
    ? Found a generic form of the rate equation for <xsl:value-of select="name()"/>, using expression: <xsl:value-of select="$expr" /><xsl:text>
                    </xsl:text>  
                    <xsl:if test="string($xmlFileUnitSystem) = 'SI Units'">
    ? Note: Equation (and all ChannelML file values) in <xsl:value-of select="$xmlFileUnitSystem"/> so need to convert v first...<xsl:text>
    </xsl:text>
    v = v * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
            </xsl:call-template>   ? temporarily set v to units of equation...<xsl:text>
            
    </xsl:text>
                        <xsl:if test="(name()='tau' or name()='inf') and 
                      (contains(string($expr), 'alpha') or
                       contains(string($expr), 'beta'))">
    ? Equation depends on alpha/beta, so converting them too...
    alpha = alpha * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Time</xsl:with-param>
                    </xsl:call-template>  
    beta = beta * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Time</xsl:with-param>   
                    </xsl:call-template>     
                        </xsl:if>
                      
                    </xsl:if>
                    <xsl:if test="string($xmlFileUnitSystem) = 'Physiological Units' and $voltConcDependence='yes'">
    ? Equations can depend on concentration. NEURON uses 'SI Units' internally for concentration, 
    ? but ChannelML file is in Physiological Units...
    <xsl:value-of select="../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../cml:conc_dependence/@variable_name"/> / <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Concentration</xsl:with-param>
                    </xsl:call-template> <xsl:text>
    </xsl:text>  
                    </xsl:if>
                    
    <xsl:call-template name="formatExpression">
        <xsl:with-param name="variable">
            <xsl:value-of select="name()"/>
        </xsl:with-param>
        <xsl:with-param name="oldExpression">
            <xsl:value-of select="$expr" />
        </xsl:with-param>
    </xsl:call-template>
    <xsl:if test="string($xmlFileUnitSystem) = 'SI Units'">
        
        <xsl:if test="name()='alpha' or name()='beta'">
    ? Set correct units of <xsl:value-of select="name()"/> for NEURON<xsl:text>
    </xsl:text>    
    <xsl:value-of select="name()"/> = <xsl:value-of select="name()"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">InvTime</xsl:with-param>
                        </xsl:call-template>
        </xsl:if>  
                                      
        <xsl:if test="name()='tau'">
    ? Set correct units of <xsl:value-of select="name()"/> for NEURON<xsl:text>
    </xsl:text>
    <xsl:value-of select="name()"/> = <xsl:value-of select="name()"/> * <xsl:call-template name="convert">
                    <xsl:with-param name="value">1</xsl:with-param>
                    <xsl:with-param name="quantity">Time</xsl:with-param>
                </xsl:call-template>
        </xsl:if> 
    
    v = v * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template>   ? reset v
        <xsl:if test="(name()='tau' or name()='inf') and 
                      (contains(string($expr), 'alpha') or
                       contains(string($expr), 'beta'))">
    alpha = alpha * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvTime</xsl:with-param>
                    </xsl:call-template>  ? resetting alpha
    beta = beta * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvTime</xsl:with-param>   
                    </xsl:call-template>  ? resetting beta
        </xsl:if>
    </xsl:if>
                    <xsl:if test="string($xmlFileUnitSystem) = 'Physiological Units' and $voltConcDependence='yes'">
    ? Resetting concentration...
    <xsl:value-of select="../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Concentration</xsl:with-param>
                    </xsl:call-template>  <xsl:text>
    </xsl:text>  
                    </xsl:if>      <xsl:text>
    </xsl:text>  
           
            </xsl:when>
            <xsl:otherwise>
    ? ERROR: Unrecognised form of the rate equation for <xsl:value-of select="name()"/>
            
            </xsl:otherwise>
        </xsl:choose>
                
       <xsl:if test="name()='tau'">
    <xsl:value-of select="$stateName"/>tau = tau/temp_adj_<xsl:value-of select="$stateName"/><xsl:text>
    </xsl:text>   
       </xsl:if>    
                   
       <xsl:if test="name()='inf'">
    <xsl:value-of select="$stateName"/>inf = inf<xsl:text>
    </xsl:text>   
       </xsl:if>
      </xsl:if>
    </xsl:for-each>
    
    <!-- Finishing off the alpha & beta to tau & inf conversion... -->

         
        <xsl:if test="count(cml:transition/cml:voltage_gate/cml:tau)=0 and count(cml:transition/cml:voltage_conc_gate/cml:tau)=0">
    <xsl:value-of select="$stateName"/>tau = 1/(temp_adj_<xsl:value-of select="$stateName"/>*(alpha + beta))<xsl:text>
    </xsl:text>
       </xsl:if>       
         
       <xsl:if test="count(cml:transition/cml:voltage_gate/cml:inf)=0 and count(cml:transition/cml:voltage_conc_gate/cml:inf)=0">
    <xsl:value-of select="$stateName"/>inf = alpha/(alpha + beta)<xsl:text>
    </xsl:text>
       </xsl:if>      
       
    
    ?     *** Finished rate equations for gate: <xsl:value-of select="$stateName"/> ***
    
        </xsl:for-each>  <!-- <xsl:for-each select='../../../../cml:hh_gate[@state=$stateName]'>-->

    </xsl:for-each> <!--<xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">-->
    
    
    
                   <!-- post v1.7.3 format -->
                   
    <xsl:for-each select='cml:current_voltage_relation/cml:conc_dependence'>
    ? Gate depends on the concentration of <xsl:value-of select="@ion"/><xsl:text>
    </xsl:text>   
    <xsl:value-of select="@variable_name"/> = <xsl:value-of select="@ion"/>i ? In NEURON, the variable for the concentration  of <xsl:value-of select="@ion"/> is <xsl:value-of select="@ion"/>i
    </xsl:for-each>
    
    <xsl:for-each select="cml:current_voltage_relation/cml:gate">  

        <xsl:variable name="gateName" select="@name"/>
        <xsl:variable name="isKSgate" select="count(cml:closed_state) + count(cml:open_state) &gt; 2"/>
            
                
       <!-- <xsl:for-each select='cml:conc_dependence'>
    ? Gate depends on the concentration of <xsl:value-of select="@ion"/><xsl:text>
    </xsl:text>   
    <xsl:value-of select="@variable_name"/> = <xsl:value-of select="@ion"/>i ? In NEURON, the variable for the concentration  of <xsl:value-of select="@ion"/> is <xsl:value-of select="@ion"/>i
    </xsl:for-each>-->
        
    ?      ***  Adding rate equations for gate: <xsl:value-of select="$gateName"/>  ***<xsl:text>
        </xsl:text>   
        
        <xsl:for-each select='cml:transition | cml:time_course | cml:steady_state'>
        
        <xsl:if  test="name()!='conc_dependence'">
            <xsl:choose>
                <xsl:when  test="@expr_form != 'generic'">
    ? Found a parameterised form of rate equation for <xsl:value-of select="@name"/>, using expression: <xsl:choose>
                                        <xsl:when test="@expr_form='exp_linear'" >A*((v-Vhalf)/B) / (1 - exp(-((v-Vhalf)/B)))</xsl:when>
                                        <xsl:when test="@expr_form='exponential'" >A*exp((v-Vhalf)/B)</xsl:when>
                                        <xsl:when test="@expr_form='sigmoid'" >A / (1 + exp((v-Vhalf)/B))</xsl:when>
                                        <xsl:otherwise >Unsupported expression type!</xsl:otherwise></xsl:choose><xsl:text>
    </xsl:text>   
    
    <xsl:variable name="A_name">A_<xsl:value-of select="@name"/>_<xsl:value-of select="$gateName"/></xsl:variable>
    <xsl:variable name="B_name">B_<xsl:value-of select="@name"/>_<xsl:value-of select="$gateName"/></xsl:variable>
    <xsl:variable name="Vhalf_name">Vhalf_<xsl:value-of select="@name"/>_<xsl:value-of select="$gateName"/></xsl:variable>
    
                    <!--<xsl:for-each select="cml:parameterised_hh/cml:parameter">
                        <xsl:if test="$favourPublicParameters = 0">
    <xsl:value-of select="@name"/>_<xsl:value-of select="name(../..)"/>_<xsl:value-of select="$gateName"/> = <xsl:value-of select="@value"/><xsl:text>
    </xsl:text></xsl:if>
                    </xsl:for-each>-->
      
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="@rate"/><xsl:text>
    </xsl:text>
    <xsl:value-of select="$B_name"/> = <xsl:value-of select="@scale"/><xsl:text>
    </xsl:text>
    <xsl:value-of select="$Vhalf_name"/> = <xsl:value-of select="@midpoint"/>
    
                    <xsl:if test="$xmlFileUnitSystem  = 'SI Units'">   
    
    ? Unit system in ChannelML file is SI units, therefore need to convert these to NEURON quanities...
    
    <xsl:choose>
                            <xsl:when test="string(name()) = 'transition'">
   <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/> * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">InvTime</xsl:with-param>
            </xsl:call-template>   ? 1/ms
    </xsl:when>
                            <xsl:when test="string(name()) = 'time_course'">
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">Time</xsl:with-param>
        </xsl:call-template>   ? ms
    </xsl:when>
                            <xsl:when test="string(name()) = 'steady_state'">
    <xsl:value-of select="$A_name"/> = <xsl:value-of select="$A_name"/>   ? Dimensionless
    </xsl:when>
    </xsl:choose>
    <xsl:value-of select="$B_name"/> = <xsl:value-of select="$B_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
          </xsl:call-template>   ? mV
    <xsl:value-of select="$Vhalf_name"/> = <xsl:value-of select="$Vhalf_name"/> * <xsl:call-template name="convert">
            <xsl:with-param name="value">1</xsl:with-param>
            <xsl:with-param name="quantity">Voltage</xsl:with-param>
          </xsl:call-template>   ? mV
          
                    </xsl:if>
    <xsl:text> 
    </xsl:text>
                    <xsl:choose>
                        <xsl:when test="@expr_form='exponential'">
    <xsl:value-of select="@name"/> = <xsl:value-of select="$A_name"/> * exp((v - <xsl:value-of select="$Vhalf_name"/>) / <xsl:value-of select="$B_name"/>)<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                        <xsl:when test="@expr_form='sigmoid'">
    <xsl:value-of select="@name"/> = <xsl:value-of select="$A_name"/> / (exp((v - <xsl:value-of select="$Vhalf_name"/>) / <xsl:value-of select="$B_name"/>) + 1)<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                        <xsl:when test="@expr_form='exp_linear'">
    <xsl:value-of select="@name"/> = <xsl:value-of select="$A_name"/> * vtrap((v - <xsl:value-of select="$Vhalf_name"/>), <xsl:value-of select="$B_name"/>)<xsl:text>
    
    </xsl:text>
                        </xsl:when>
                    </xsl:choose>
    
    
                </xsl:when>
                <xsl:when test="@expr_form = 'generic'">
                    <xsl:variable name="expr"><xsl:value-of select="@expr" /></xsl:variable> 
    ? Found a generic form of the rate equation for <xsl:value-of select="@name"/>, using expression: <xsl:value-of select="$expr" /><xsl:text>
    </xsl:text>  
                    <xsl:if test="string($xmlFileUnitSystem) = 'SI Units'">
    ? Note: Equation (and all ChannelML file values) in <xsl:value-of select="$xmlFileUnitSystem"/> so need to convert v first...<xsl:text>
    </xsl:text>
    v = v * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
            </xsl:call-template>   ? temporarily set v to units of equation...<xsl:text>
            
    </xsl:text>
                        <xsl:if test="(name()='time_course' or name()='steady_state') and 
                      (contains(string($expr), 'alpha') or
                       contains(string($expr), 'beta'))">
    ? Equation depends on alpha/beta, so converting them too...
    alpha = alpha * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Time</xsl:with-param>
                    </xsl:call-template>  
    beta = beta * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Time</xsl:with-param>   
                    </xsl:call-template>     
                        </xsl:if>
                      
                    </xsl:if>
                    <xsl:if test="string($xmlFileUnitSystem) = 'Physiological Units' and $voltConcDependence='yes'">
    ? Equations can depend on concentration. NEURON uses 'SI Units' internally for concentration, 
    ? but the ChannelML file is in Physiological Units...
    <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> / <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Concentration</xsl:with-param>
                    </xsl:call-template> <xsl:text>
    </xsl:text>  
                    </xsl:if>
                    
    <xsl:call-template name="formatExpression">
        <xsl:with-param name="variable">
            <xsl:value-of select="@name"/>
        </xsl:with-param>
        <xsl:with-param name="oldExpression">
            <xsl:value-of select="$expr" />
        </xsl:with-param>
    </xsl:call-template>
    <xsl:if test="string($xmlFileUnitSystem) = 'SI Units'">
        
        <xsl:if test="name()='transition'">
    ? Set correct units of <xsl:value-of select="@name"/> for NEURON<xsl:text>
    </xsl:text>    
    <xsl:value-of select="@name"/> = <xsl:value-of select="@name"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">InvTime</xsl:with-param>
                        </xsl:call-template>
        </xsl:if>  
                                      
        <xsl:if test="name()='time_course'">
    ? Set correct units of <xsl:value-of select="@name"/> for NEURON<xsl:text>
    </xsl:text>
    <xsl:value-of select="@name"/> = <xsl:value-of select="@name"/> * <xsl:call-template name="convert">
                    <xsl:with-param name="value">1</xsl:with-param>
                    <xsl:with-param name="quantity">Time</xsl:with-param>
                </xsl:call-template>
        </xsl:if> 
    
    v = v * <xsl:call-template name="convert">
                <xsl:with-param name="value">1</xsl:with-param>
                <xsl:with-param name="quantity">Voltage</xsl:with-param>
            </xsl:call-template>   ? reset v
        <xsl:if test="(name()='transition' or name()='steady_state') and 
                      (contains(string($expr), 'alpha') or
                       contains(string($expr), 'beta'))">
    alpha = alpha * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvTime</xsl:with-param>
                    </xsl:call-template>  ? resetting alpha
    beta = beta * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvTime</xsl:with-param>   
                    </xsl:call-template>  ? resetting beta
        </xsl:if>
    </xsl:if>
                    <xsl:if test="string($xmlFileUnitSystem) = 'Physiological Units' and $voltConcDependence='yes'">
    ? Resetting concentration...
    <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Concentration</xsl:with-param>
                    </xsl:call-template>  <xsl:text>
    </xsl:text>  
                    </xsl:if>      <xsl:text>
    </xsl:text>  
           
            </xsl:when>
            <xsl:otherwise>
    ? ERROR: Unrecognised form of the rate equation for <xsl:value-of select="@name"/>
            
            </xsl:otherwise>
        </xsl:choose>

       <xsl:if test="name()='transition' and boolean($isKSgate)">
    <xsl:value-of select="@name"/> = <xsl:value-of select="@name"/> * temp_adj_<xsl:value-of select="$gateName"/>   ? Applying temp adj here as channel has KS description<xsl:text>
    </xsl:text>
       </xsl:if>

       <xsl:if test="name()='time_course'">
    <xsl:value-of select="@to"/>tau = tau/temp_adj_<xsl:value-of select="@to"/><xsl:text>
    </xsl:text>
       </xsl:if>
                   
       <xsl:if test="name()='steady_state'">
    <xsl:value-of select="@to"/>inf = inf<xsl:text>
    </xsl:text>   
       </xsl:if>
      </xsl:if>
      </xsl:for-each>
    <!--</xsl:if>-->
    
    <!-- Finishing off the alpha & beta to tau & inf conversion... -->

    <xsl:if test="not(boolean($isKSgate))">
        <xsl:if test="count(cml:time_course)=0">
    <xsl:value-of select="$gateName"/>tau = 1/(temp_adj_<xsl:value-of select="$gateName"/>*(alpha + beta))<xsl:text>
    </xsl:text>
       </xsl:if>       
         
       <xsl:if test="count(cml:steady_state)=0">
    <xsl:value-of select="$gateName"/>inf = alpha/(alpha + beta)<xsl:text>
    </xsl:text>
       </xsl:if>
    </xsl:if>


    ?     *** Finished rate equations for gate: <xsl:value-of select="$gateName"/> ***
    

    </xsl:for-each> <!--<xsl:for-each select="cml:current_voltage_relation/cml:gate">-->
}

<xsl:if test="count(cml:hh_gate/cml:transition/cml:voltage_gate/*/cml:parameterised_hh[@type='linoid']) &gt; 0 or
              count(cml:current_voltage_relation/cml:gate/*[@expr_form='exp_linear']) &gt; 0">
? Function to assist with parameterised expressions of type linoid/exp_linear

FUNCTION vtrap(VminV0, B) {
    if (fabs(VminV0/B) &lt; 1e-6) {
    vtrap = (1 + VminV0/B/2)
}else{
    vtrap = (VminV0 / B) /(1 - exp((-1 *VminV0)/B))
    }
}
</xsl:if>
UNITSON


</xsl:if>

</xsl:template> <!--end of <xsl:template match="cml:channel_type">-->


<xsl:template match="cml:ion_concentration">
<!-- Based on Louise Whiteley's implementation of this while on rotation in the Silver Lab-->
? Creating ion concentration

TITLE Channel: <xsl:value-of select="@name"/>

<xsl:if test="count(meta:notes) &gt; 0">

COMMENT
    <xsl:value-of select="meta:notes"/>
ENDCOMMENT
</xsl:if>

UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
    (um) = (micrometer)
    (l) = (liter)
    (molar) = (1/liter)
    (mM) = (millimolar)
}

    
NEURON {
    SUFFIX <xsl:value-of select="@name"/>
    
    <xsl:for-each select="/cml:channelml/cml:ion[@name!='non_specific']">
    USEION <xsl:value-of select="@name"/> READ i<xsl:value-of select="@name"/> WRITE <xsl:value-of select="@name"/>i VALENCE <xsl:value-of select="@charge"/>
  
    </xsl:for-each>
    
    <xsl:variable name="ionused"><xsl:value-of select="cml:ion_species"/><xsl:value-of select="cml:ion_species/@name"/></xsl:variable>
    <xsl:variable name="valency"><xsl:value-of select="/cml:channelml/cml:ion[@name=$ionused]/@charge"/></xsl:variable>
    
    RANGE <xsl:value-of select="$ionused"/>i
    
    RANGE rest_conc
    
    <xsl:if test="count(cml:decaying_pool_model/cml:decay_constant) &gt; 0 or count(cml:decaying_pool_model/@decay_constant) &gt; 0">
    RANGE tau
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:inv_decay_constant) &gt; 0 or count(cml:decaying_pool_model/@inv_decay_constant) &gt; 0">
    RANGE beta
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:ceiling) &gt; 0 or count(cml:decaying_pool_model/@ceiling) &gt; 0">
    RANGE ceiling
    </xsl:if>
    
    <xsl:if test="count(cml:decaying_pool_model/cml:pool_volume_info) &gt; 0">
    RANGE thickness, F


    RANGE total_current
    RANGE volume_pool
    
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:fixed_pool_info) &gt; 0">
    RANGE phi
    </xsl:if>
    
}

ASSIGNED {

    i<xsl:value-of select="$ionused"/> (mA/cm2)
    diam (um)
    area (um)
}

INITIAL {
    <xsl:if test="count(cml:decaying_pool_model/cml:pool_volume_info) &gt; 0">
        
    LOCAL pi, shell_inner_diam, cylinderLen, circumference, circumference_shell, volumeOuter, volumeInner, volumeSph, volumeCyl

    pi = 3.14159265

    shell_inner_diam = diam - (2*thickness)


    ?  Volume of the pool if it is a shell inside a sphere of diameter diam

    volumeSph = (diam*diam*diam) * pi / 6 - (shell_inner_diam*shell_inner_diam*shell_inner_diam)* pi / 6


    ? Volume of the pool if it is a cylinder

    circumference = diam * pi
    circumference_shell = shell_inner_diam * pi

    cylinderLen = area/circumference

    volumeOuter = (diam * diam/4) * pi * cylinderLen
    volumeInner = (shell_inner_diam * shell_inner_diam/4) * pi * cylinderLen
    volumeCyl = volumeOuter - volumeInner

    if ((area - (pi * diam * diam)) &lt; 1e-3 &amp;&amp; (area - (pi * diam * diam)) &gt; -1e-3 ) {

        ? Assume the segment is a sphere
        <xsl:if test="$debug = 1">printf("+++++++ Assume a sphere: %g, %g, %g\n", area, (pi * diam * diam), (area - (pi * diam * diam)))</xsl:if>

        volume_pool = volumeSph
        
    } else {

        ? assume segment is a cylinder
        <xsl:if test="$debug = 1">printf("+++++++ Assume a cylinder: %g, %g, %g\n", area, (pi * diam * diam), (area - (pi * diam * diam)))</xsl:if>

        volume_pool = volumeCyl
    }

    <xsl:if test="$debug = 1">printf("+++++++ Init ca, diam: %g, cylinderLen: %g, volume_pool: %g, volumeSph: %g, volumeCyl: %g, area as sph: %g, area x d: %g, area: %g\n", diam, cylinderLen, volume_pool, volumeSph, volumeCyl, (pi * diam * diam), (area*thickness), area)</xsl:if>
    
    </xsl:if>
    <xsl:value-of select="$ionused"/>i = rest_conc

}

PARAMETER {

    total_current
    rest_conc = <xsl:call-template name="convert">
                    <xsl:with-param name="value">
                        <xsl:value-of select="cml:decaying_pool_model/cml:resting_conc"/><xsl:value-of select="cml:decaying_pool_model/@resting_conc"/> <!-- Either element or attr will be present...-->
                    </xsl:with-param>
              <xsl:with-param name="quantity">Concentration</xsl:with-param>
          </xsl:call-template> (mM)
          
    <xsl:if test="count(cml:decaying_pool_model/cml:decay_constant) &gt; 0 or count(cml:decaying_pool_model/@decay_constant) &gt; 0">
    tau = <xsl:call-template name="convert">
              <xsl:with-param name="value">
                  <xsl:value-of select="cml:decaying_pool_model/cml:decay_constant"/><xsl:value-of select="cml:decaying_pool_model/@decay_constant"/>  <!-- Either element or attr will be present...-->
              </xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param>
          </xsl:call-template> (ms)
   </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:inv_decay_constant) &gt; 0 or count(cml:decaying_pool_model/@inv_decay_constant) &gt; 0">
    beta = <xsl:call-template name="convert">
              <xsl:with-param name="value">
                  <xsl:value-of select="cml:decaying_pool_model/cml:inv_decay_constant"/><xsl:value-of select="cml:decaying_pool_model/@inv_decay_constant"/>  <!-- Either element or attr will be present...-->
              </xsl:with-param>
              <xsl:with-param name="quantity">InvTime</xsl:with-param>
          </xsl:call-template> (/ms)
   </xsl:if>
          
    <xsl:if test="count(cml:decaying_pool_model/cml:ceiling) &gt; 0 or count(cml:decaying_pool_model/@ceiling) &gt; 0">
    ceiling = <xsl:call-template name="convert">
                    <xsl:with-param name="value">
                        <xsl:value-of select="cml:decaying_pool_model/cml:ceiling"/><xsl:value-of select="cml:decaying_pool_model/@ceiling"/>  <!-- Either element or attr will be present...-->
                    </xsl:with-param>
              <xsl:with-param name="quantity">Concentration</xsl:with-param>
          </xsl:call-template> (mM)
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:pool_volume_info) &gt; 0">
    F = 96494 (C)
    
    thickness = <xsl:call-template name="convert">
                    <xsl:with-param name="value">
                        <xsl:value-of select="cml:decaying_pool_model/cml:pool_volume_info/cml:shell_thickness"/><xsl:value-of select="cml:decaying_pool_model/cml:pool_volume_info/@shell_thickness"/>
                    </xsl:with-param>
                    <xsl:with-param name="quantity">Length</xsl:with-param>
                </xsl:call-template> (um)   
                
    volume_pool
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:fixed_pool_info) &gt; 0">
    phi = <xsl:value-of select="cml:decaying_pool_model/cml:fixed_pool_info/cml:phi"/>
    </xsl:if>
    
}

STATE {

    <xsl:value-of select="$ionused"/>i (mM)

}

BREAKPOINT {

    SOLVE conc METHOD derivimplicit
    <xsl:if test="count(cml:decaying_pool_model/cml:ceiling) &gt; 0 or count(cml:decaying_pool_model/@ceiling) &gt; 0">
    if( <xsl:value-of select="$ionused"/>i &lt; 0 ){ <xsl:value-of select="$ionused"/>i = 0 }
    if( <xsl:value-of select="$ionused"/>i &gt; ceiling ){ <xsl:value-of select="$ionused"/>i = ceiling }
    </xsl:if>

}

DERIVATIVE conc {
    <xsl:variable name="timeConstFactor"><xsl:choose>
        <xsl:when test="count(cml:decaying_pool_model/cml:inv_decay_constant) &gt; 0 or count(cml:decaying_pool_model/@inv_decay_constant) &gt; 0">* beta</xsl:when>
        <xsl:otherwise>/tau</xsl:otherwise></xsl:choose>
    </xsl:variable>
    <xsl:if test="count(cml:decaying_pool_model/cml:pool_volume_info) &gt; 0">
    LOCAL thickness_cm, surf_area_cm2, volume_cm3 ? Note, normally dimensions are in um, but curr dens is in mA/cm2, etc
    
    thickness_cm = thickness *(1e-4)
    surf_area_cm2 = area * 1e-8
    volume_cm3 = volume_pool * 1e-12
    
    total_current = i<xsl:value-of select="$ionused"/> * surf_area_cm2


    <xsl:value-of select="$ionused"/>i' =  ((-1 * total_current)/(<xsl:value-of select="$valency"/> * F * volume_cm3)) - ((<xsl:value-of select="$ionused"/>i - rest_conc)<xsl:value-of select="$timeConstFactor"/>)
    </xsl:if>
    <xsl:if test="count(cml:decaying_pool_model/cml:fixed_pool_info) &gt; 0">
    <xsl:value-of select="$ionused"/>i' = - (phi * i<xsl:value-of select="$ionused"/>) - ((<xsl:value-of select="$ionused"/>i - rest_conc)<xsl:value-of select="$timeConstFactor"/>)
    </xsl:if>

}

</xsl:template>  <!--<xsl:template match="cml:ion_concentration">-->


<!-- Function to get value converted to proper units.-->
<xsl:template name="convert">
    <xsl:param name="value" />
    <xsl:param name="quantity" />
    <xsl:choose> 
        <xsl:when test="$xmlFileUnitSystem  = 'Physiological Units'">
            <xsl:choose>
                <xsl:when test="$quantity = 'Conductance Density'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Conductance'"><xsl:value-of select="number($value) * 1000"/></xsl:when>
                <xsl:when test="$quantity = 'Voltage'"><xsl:value-of select="$value"/></xsl:when>                       <!-- same -->
                <xsl:when test="$quantity = 'InvVoltage'"><xsl:value-of select="$value"/></xsl:when>                    <!-- same -->
                <xsl:when test="$quantity = 'Time'"><xsl:value-of select="number($value)"/></xsl:when>                  <!-- same -->
                <xsl:when test="$quantity = 'Length'"><xsl:value-of select="number($value * 10000)"/></xsl:when>        <!-- same -->
                <xsl:when test="$quantity = 'InvTime'"><xsl:value-of select="number($value)"/></xsl:when>               <!-- same --> 
                <xsl:when test="$quantity = 'Concentration'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvConcentration'"><xsl:value-of select="number($value div 1000000)"/></xsl:when>

                <xsl:otherwise><xsl:value-of select="number($value)"/></xsl:otherwise>
            </xsl:choose>
        </xsl:when>           
        <xsl:when test="$xmlFileUnitSystem  = 'SI Units'">
            <xsl:choose>
                <xsl:when test="$quantity = 'Conductance Density'"><xsl:value-of select="number($value div 10000)"/></xsl:when>
                <xsl:when test="$quantity = 'Conductance'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'Voltage'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvVoltage'"><xsl:value-of select="$value div 1000"/></xsl:when>
                <xsl:when test="$quantity = 'Length'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'Time'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvTime'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Concentration'"><xsl:value-of select="number($value)"/></xsl:when>         <!-- same -->
                <xsl:when test="$quantity = 'InvConcentration'"><xsl:value-of select="number($value)"/></xsl:when>      <!-- same -->

                <xsl:otherwise><xsl:value-of select="number($value)"/></xsl:otherwise>
            </xsl:choose>
        </xsl:when>   
    </xsl:choose>
</xsl:template>







<xsl:template match="cml:synapse_type">
    <xsl:if test="count(cml:doub_exp_syn)>0">
? Creating synaptic mechanism, based on NEURON source impl of Exp2Syn
    </xsl:if>
    <xsl:if test="count(cml:blocking_syn)>0">
? Creating NMDA like synaptic mechanism, based on NEURON source impl of Exp2Syn
    </xsl:if>
    <xsl:if test="count(cml:multi_decay_syn)>0">
? Creating synaptic mechanism, based on Volker Steuber &amp; Chiara Saviane implementation of 3 decay component facilitating synapse
    </xsl:if>
    <xsl:if test="count(cml:electrical_syn)>0">
? Creating synaptic mechanism for an electrical synapse
    </xsl:if>
    <xsl:if test="count(cml:fac_dep_syn)>0">
? Creating synaptic mechanism, based on Volker Steuber &amp; Chiara Saviane implementation of 3 decay component facilitating synapse
    </xsl:if>
    <xsl:if test="count(cml:stdp_syn)>0">
? Creating synaptic mechanism, based on Andrew Davison's impl of Song and Abbot's STDP model
    </xsl:if>
    <xsl:variable name="hasMultiDecay">
        <xsl:choose>
            <xsl:when test="count(cml:multi_decay_syn)>0 or 
                            (count(cml:fac_dep_syn)>0 and count(cml:fac_dep_syn/@max_conductance_2)>0) or 
                            (count(cml:stdp_syn)>0 and count(cml:stdp_syn/@max_conductance_2)>0)">yes</xsl:when>
            <xsl:otherwise>no</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

TITLE Channel: <xsl:value-of select="@name"/>

<xsl:if test="count(meta:notes) &gt; 0">

COMMENT
    <xsl:value-of select="meta:notes"/>
ENDCOMMENT
</xsl:if>

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (uS) = (microsiemens)
}

    
NEURON {
    POINT_PROCESS <xsl:value-of select="@name"/>
    
<xsl:choose>
    <xsl:when test="count(cml:electrical_syn)>0">
    NONSPECIFIC_CURRENT i
    RANGE g, i
    RANGE weight
    <xsl:choose>
        <xsl:when test="$parallelMode = 1">
    RANGE vgap     : Using a RANGE variable as opposed to POINTER for parallel mode
        </xsl:when>
        <xsl:otherwise>
    POINTER vgap  : Using a POINTER as opposed to RANGE for serial mode
        </xsl:otherwise>
        </xsl:choose>
        
    </xsl:when>
    <xsl:otherwise>
    RANGE tau_rise, tau_decay 
    GLOBAL total
    
<xsl:if test="count(cml:blocking_syn)>0">
    RANGE <xsl:value-of select="cml:blocking_syn/cml:block/@species"/>_conc, eta, gamma, gblock
    GLOBAL total
</xsl:if>

<xsl:if test="$hasMultiDecay = 'yes'">
    RANGE tau_decay_2, tau_decay_3, gmax_2, gmax_3, ampl
</xsl:if>
<xsl:if test="count(cml:fac_dep_syn)>0">
    RANGE tau_rec           : time course of recovery from synaptic depression
    RANGE tau_facil         : time course of facilitation
    RANGE U, Uinit          : release probability and initial value
</xsl:if>
<xsl:if test="count(cml:stdp_syn)>0">
    RANGE post_spike_thresh            : voltage at which post syn cell will be considered spiking
    RANGE t_post_spike, t_pre_spike    : times of last post and pre spikes
    RANGE stdp_weight_factor           : multiplicative factor for weight which changes based on activity
    
    RANGE M, P
    RANGE wmax                         : maximum synaptic weight which can be reached
    RANGE del_weight_ltp, del_weight_ltd                   : 
    
    RANGE tau_ltp, tau_ltd
</xsl:if>

    RANGE i, e, gmax
    NONSPECIFIC_CURRENT i
    RANGE g, factor<xsl:if test="count(cml:multi_decay_syn)>0">, factor_2, factor_3</xsl:if>
    </xsl:otherwise>
</xsl:choose>

}

PARAMETER {<xsl:for-each select="cml:doub_exp_syn | cml:blocking_syn | cml:multi_decay_syn | cml:fac_dep_syn | cml:stdp_syn">
    gmax = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="@max_conductance"/></xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template>
    tau_rise = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="@rise_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt;1e-9,1e9&gt;
    tau_decay = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="@decay_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt;1e-9,1e9&gt;
    e = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="@reversal_potential"/></xsl:with-param>
              <xsl:with-param name="quantity">Voltage</xsl:with-param></xsl:call-template>  (mV)
</xsl:for-each>
<xsl:for-each select="cml:blocking_syn">
    <xsl:value-of select="cml:block/@species"/>_conc = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:block/@conc"/></xsl:with-param>
              <xsl:with-param name="quantity">Concentration</xsl:with-param></xsl:call-template> 
              
    eta = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:block/@eta"/></xsl:with-param>
              <xsl:with-param name="quantity">InvConcentration</xsl:with-param></xsl:call-template> 
              
    gamma = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:block/@gamma"/></xsl:with-param>
              <xsl:with-param name="quantity">InvVoltage</xsl:with-param></xsl:call-template> 
              
</xsl:for-each>
<xsl:if test="$hasMultiDecay = 'yes'">
    <xsl:for-each select="cml:multi_decay_syn | cml:fac_dep_syn | cml:stdp_syn">
        <xsl:choose>
            <xsl:when test="count(@decay_time_2) &gt; 0 and count(@max_conductance_2) &gt; 0">     
    gmax_2 = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:choose>
                                    <xsl:when test="count(@max_conductance_2)>0"><xsl:value-of select="@max_conductance_2"/></xsl:when>
                                    <xsl:otherwise>0</xsl:otherwise></xsl:choose>
              </xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template> 
              
    tau_decay_2 = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:choose>
                                    <xsl:when test="count(@decay_time_2)>0"><xsl:value-of select="@decay_time_2"/></xsl:when>
                                    <xsl:otherwise>0</xsl:otherwise></xsl:choose>
              </xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt;1e-9,1e9&gt;
            </xsl:when>
            <xsl:otherwise>
    gmax_2 = 0
    tau_decay_2 = 100000
            </xsl:otherwise>  
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="count(@decay_time_3) &gt; 0 and count(@max_conductance_3) &gt; 0">     
        
    gmax_3 = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:choose>
                                    <xsl:when test="count(@max_conductance_3)>0"><xsl:value-of select="@max_conductance_3"/></xsl:when>
                                    <xsl:otherwise>0</xsl:otherwise></xsl:choose>
              </xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template> 
              
    tau_decay_3 = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:choose>
                                    <xsl:when test="count(@decay_time_3)>0"><xsl:value-of select="@decay_time_3"/></xsl:when>
                                    <xsl:otherwise>0</xsl:otherwise></xsl:choose>
                </xsl:with-param>
                <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt;1e-9,1e9&gt;
            </xsl:when>
            <xsl:otherwise>
    gmax_3 = 0
    tau_decay_3 = 100000
            </xsl:otherwise>            
        </xsl:choose>
    </xsl:for-each>
</xsl:if>
     
<xsl:for-each select="cml:multi_decay_syn | cml:fac_dep_syn | cml:stdp_syn">         
    <xsl:if test="count(cml:plasticity)>0">
    tau_rec = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:plasticity/@tau_rec"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt; 1e-9, 1e9 &gt; 
    tau_facil = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:plasticity/@tau_fac"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt; 0 ,1e9 &gt; 
              
    Uinit = <xsl:value-of select="cml:plasticity/@init_release_prob"/> (1)  &lt; 0, 1 &gt; :release probability
    
    </xsl:if>
    <xsl:if test="count(cml:spike_time_dep)>0">
    tau_ltp=<xsl:call-template name="convert">
          <xsl:with-param name="value"><xsl:value-of select="cml:spike_time_dep/@tau_ltp"/></xsl:with-param>
          <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt; 1e-9, 1e9 &gt; 
    tau_ltd=<xsl:call-template name="convert">
          <xsl:with-param name="value"><xsl:value-of select="cml:spike_time_dep/@tau_ltd"/></xsl:with-param>
          <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> (ms) &lt; 1e-9, 1e9 &gt; 

    del_weight_ltp=<xsl:value-of select="cml:spike_time_dep/@del_weight_ltp"/> (1) &lt; 0, 1e9 &gt; 
    del_weight_ltd=<xsl:value-of select="cml:spike_time_dep/@del_weight_ltd"/> (1) &lt; 0, 1e9 &gt; 
    
    wmax=<xsl:value-of select="cml:spike_time_dep/@max_syn_weight"/> (1) &lt; 0, 1e9 &gt; 
    
       
    post_spike_thresh = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:spike_time_dep/@post_spike_thresh"/></xsl:with-param>
              <xsl:with-param name="quantity">Voltage</xsl:with-param></xsl:call-template>  (mV)
              
    in_post_spike = 0   : 1 if post cell is spiking, 0 otherwise
    </xsl:if>
</xsl:for-each>
<xsl:for-each select="cml:electrical_syn">
    v (millivolt)
    vgap (millivolt)
    g = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="@conductance"/></xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template> (microsiemens)
    weight = 1
</xsl:for-each>
}

<xsl:if test="count(cml:electrical_syn)>0">
ASSIGNED {
    i (nanoamp)
}

BREAKPOINT {
    i = weight * g * (v - vgap)
} 
</xsl:if>

<xsl:if test="count(cml:doub_exp_syn)>0 or count(cml:blocking_syn)>0 or count(cml:multi_decay_syn)>0  or count(cml:fac_dep_syn)>0  or count(cml:stdp_syn)>0 ">
ASSIGNED {
    v (mV)
    i (nA)
    g (uS)
    factor <xsl:if test="$hasMultiDecay = 'yes'">
    factor_2
    factor_3
    </xsl:if>
    total (uS)
<xsl:if test="count(cml:fac_dep_syn)>0 ">
    R
    U</xsl:if>
<xsl:if test="count(cml:blocking_syn)>0">    gblock</xsl:if>
<xsl:if test="count(cml:stdp_syn)>0">
    M              
    P              
    deltaw        
    t_post_spike (ms)
    t_pre_spike  (ms)
    stdp_weight_factor
</xsl:if>
}

STATE {
    A (uS)
    B (uS)<xsl:if test="$hasMultiDecay = 'yes'">
    C (uS)
    D (uS)</xsl:if>
}

INITIAL {
    LOCAL tp<xsl:if test="$hasMultiDecay = 'yes'">, tp_2, tp_3</xsl:if>
    total = 0
    
    if (tau_rise == 0) {
        tau_rise = 1e-9  : will effectively give a single exponential timecourse synapse
    }
    
    if (tau_rise/tau_decay > .999999) {
        tau_rise = .999999*tau_decay : will result in an "alpha" synapse waveform
    }
    A = 0
    B = 0<xsl:if test="$hasMultiDecay = 'yes'">
    C = 0
    D = 0
    </xsl:if>
    tp = (tau_rise*tau_decay)/(tau_decay - tau_rise) * log(tau_decay/tau_rise)
    factor = -exp(-tp/tau_rise) + exp(-tp/tau_decay)
    factor = 1/factor<xsl:if test="$hasMultiDecay = 'yes'">
        
    tp_2 = (tau_rise*tau_decay_2)/(tau_decay_2 - tau_rise) * log(tau_decay_2/tau_rise)
    factor_2 = -exp(-tp_2/tau_rise) + exp(-tp_2/tau_decay_2)
    factor_2 = 1/factor_2
    
    tp_3 = (tau_rise*tau_decay_3)/(tau_decay_3 - tau_rise) * log(tau_decay_3/tau_rise)
    factor_3 = -exp(-tp_3/tau_rise) + exp(-tp_3/tau_decay_3)
    factor_3 = 1/factor_3
    </xsl:if>
    <xsl:if test="count(cml:fac_dep_syn)>0 ">
    </xsl:if>
    <xsl:if test="count(cml:stdp_syn)>0 ">
        
    M = 0
    P = 0
    deltaw = 0
    t_post_spike = 0
    t_pre_spike = 0
    stdp_weight_factor = 1
    </xsl:if>
}

BREAKPOINT {
    SOLVE state METHOD cnexp
    <xsl:choose>
    <xsl:when test="count(cml:blocking_syn)>0">gblock = 1 / (1+ (<xsl:value-of select="cml:blocking_syn/cml:block/@species"/>_conc * eta * exp(-1 * gamma * v)))
    g = gmax * gblock * (B - A)</xsl:when>
    <xsl:when test="$hasMultiDecay = 'yes'">g = (gmax * (B - A)) + (gmax_2 * (C - A)) + (gmax_3 * (D - A))</xsl:when>
    <xsl:otherwise>g = gmax * (B - A)</xsl:otherwise>
    </xsl:choose>
    i = g*(v - e)
    <!--
    <xsl:if test="count(cml:stdp_syn)>0 ">
    
    if (in_post_spike == 0 &amp;&amp; v >= post_spike_thresh) {
        printf(" t: %g, v: %g\n", t, v)
        <xsl:if test="$debug = 1">printf("\n...............\n")
        printf(" POST SPIKE, t: %g, P: %g, M: %g, v: %g, in_post_spike: %g\n", t, P, M, v, in_post_spike)
        
        if (t_post_spike >= 0) {
            printf(".. Last post spike ago: %g\n", t - t_post_spike)
        }    
        if (t_pre_spike >= 0) {
            printf(".. Last pre spike ago: %g\n", t - t_pre_spike)
        }</xsl:if>
        
        M = M * exp((t_post_spike-t)/tau_ltd) - del_weight_ltd

        if (t_pre_spike >= 0) {
            deltaw = wmax * P * exp(-(t - t_pre_spike)/tau_ltp)
        }
        
        stdp_weight_factor = stdp_weight_factor + deltaw
        <xsl:if test="$debug = 1">
        printf(".. stdp_weight_factor: %g, deltaw: %g, P: %g, M: %g\n", stdp_weight_factor, deltaw, P, M)
        </xsl:if>
        
        t_post_spike = t
        in_post_spike = 1
    }

    if (in_post_spike == 1 &amp;&amp; v &lt; post_spike_thresh &amp;&amp; t > (t_post_spike+0.1)) { : TODO: check need for this 0.1
        <xsl:if test="$debug = 1">
        printf(".. in_post_spike no longer at :%g, v: %g\n", t, v)
        </xsl:if>
        in_post_spike = 0
    }
    
    </xsl:if>-->
}


DERIVATIVE state {
    A' = -A/tau_rise
    B' = -B/tau_decay <xsl:if test="$hasMultiDecay = 'yes'">
    C' = -C/tau_decay_2
    D' = -D/tau_decay_3
    </xsl:if>
}

NET_RECEIVE(weight (uS)<xsl:if test="count(cml:fac_dep_syn)>0 ">, U, R, tsyn (ms)</xsl:if>) {
    <xsl:if test="count(cml:fac_dep_syn)>0 ">
    LOCAL RUD
    
    INITIAL {
        tsyn = -1
        <xsl:if test="$debug = 1">printf("-- In the INITIAL statement in NET_RECEIVE\n")</xsl:if>
        U = Uinit
        R = 1
        <xsl:if test="$debug = 1">printf("-- t: %g, delt: %g, g: %g, U: %g, R: %g\n", t, t-tsyn, g, U, R)</xsl:if>
    }

    <xsl:if test="$debug = 1">printf("------------------------------------------------------------\n")</xsl:if>
    <xsl:if test="$debug = 1">
        printf("-- t: %g, delt: %g, g: %g, U: %g, R: %g\n", t, t-tsyn, g, U, R)
    </xsl:if>

    if (tsyn > 0) {
    
        R = R * (1-U) * exp(-(t - tsyn)/tau_rec) + 1 - exp(-(t - tsyn)/tau_rec)

        if (tau_facil > 0) {
            U = U * exp(-(t - tsyn)/tau_facil) + Uinit * (1 - (U * exp(-(t - tsyn)/tau_facil)))
        } else {
            U = Uinit
        }
    
    } else {
        <xsl:if test="$debug = 1">printf("-- At first spike...\n")</xsl:if>
    }
        
    RUD = (U*R)

    <xsl:if test="$debug = 1">printf("-- t: %g, delt: %g, g: %g, U: %g, R: %g, RUD: %g\n", t, t-tsyn, g, U, R, RUD)</xsl:if>

    </xsl:if>

    <xsl:if test="$debug = 1">printf("------------------------------------------------------------\n")
    </xsl:if>
    
    <xsl:if test="$debug = 1">printf("-- SPIKE at time: %f (%g), with weight %g!\n", t, t, weight)
    </xsl:if>
    
    <xsl:if test="count(cml:stdp_syn)>0 ">
    <xsl:if test="$debug = 1">
    if (t_post_spike >= 0) {
        printf("-- Last post spike ago: %g\n", t-t_post_spike)
    }    
    if (t_pre_spike >= 0) {
        printf("-- Last pre spike ago: %g\n", t-t_pre_spike)
    }</xsl:if>
    
    if (weight >= 0) {               : this is a pre-synaptic spike
    
        P = P*exp((t_pre_spike-t)/tau_ltp) + del_weight_ltp
                        
        deltaw = wmax * M * exp((t_post_spike - t)/tau_ltd)
        
        t_pre_spike = t
    
    } else {                : this is a post-synaptic spike
    
        M = M*exp((t_post_spike-t)/tau_ltd) - del_weight_ltd

        //Todo: double check this!
        //?  deltaw = wmax * P * exp(-(t - t_pre_spike)/tau_ltp)
        deltaw = deltaw + wmax * P * exp(-(t - t_pre_spike)/tau_ltp)
        
        t_post_spike = t
        
    }
    
    
    

    stdp_weight_factor = stdp_weight_factor + deltaw
    
    if (stdp_weight_factor > wmax) { stdp_weight_factor = wmax}
    if (stdp_weight_factor &lt; 0)    { stdp_weight_factor = 0}

    
    printf("pg-- stdp_weight_factor: %g, deltaw: %g, P: %g, M: %g\n", stdp_weight_factor,deltaw, P, M)
    
    if (weight >= 0) {               : this is a pre-synaptic spike
    </xsl:if>
    
    
    <xsl:choose>
        <xsl:when test="$hasMultiDecay = 'yes'"> LOCAL Ajump, Bjump, Cjump, Djump
    Bjump = weight*factor<xsl:if test="count(cml:stdp_syn)>0 ">*stdp_weight_factor</xsl:if>
    Cjump = weight*factor_2<xsl:if test="count(cml:stdp_syn)>0 ">*stdp_weight_factor</xsl:if>
    Djump = weight*factor_3<xsl:if test="count(cml:stdp_syn)>0 ">*stdp_weight_factor</xsl:if>
    
    Ajump = (gmax*Bjump + gmax_2*Cjump + gmax_3*Djump)/(gmax + gmax_2 + gmax_3)
    
    state_discontinuity(A, A + Ajump)
    state_discontinuity(B, B + Bjump)
    state_discontinuity(C, C + Cjump)
    state_discontinuity(D, D + Djump)
        </xsl:when>
        <xsl:otherwise>
    state_discontinuity(A, A + weight*factor<xsl:if test="count(cml:fac_dep_syn)>0 ">*RUD</xsl:if><xsl:if test="count(cml:stdp_syn)>0 ">*stdp_weight_factor</xsl:if>)
    state_discontinuity(B, B + weight*factor<xsl:if test="count(cml:fac_dep_syn)>0 ">*RUD</xsl:if><xsl:if test="count(cml:stdp_syn)>0 ">*stdp_weight_factor</xsl:if>)

    </xsl:otherwise>
    </xsl:choose>
    
    
    <xsl:if test="count(cml:fac_dep_syn)>0 ">
    tsyn = t
    </xsl:if>
    <xsl:if test="count(cml:stdp_syn)>0 ">
    }
    </xsl:if>
    
}

</xsl:if>




</xsl:template>  <!--<xsl:template match="cml:synapse_type">-->


<!-- Function to try to format the rate expression to something this simulator is a bit happier with-->
<xsl:template name="formatExpression">
    <xsl:param name="variable" />
    <xsl:param name="oldExpression" />
    <xsl:choose>
        <xsl:when test="contains($oldExpression, '?')">
    <!-- Expression contains a condition!!-->
    <xsl:variable name="ifTrue"><xsl:value-of select="substring-before(substring-after($oldExpression,'?'), ':')"/></xsl:variable>
    <xsl:variable name="ifFalse"><xsl:value-of select="substring-after($oldExpression,':')"/></xsl:variable>
    
    if (<xsl:value-of select="substring-before($oldExpression,'?')"/>) {<xsl:text>
        </xsl:text><xsl:value-of select="$variable"/> = <xsl:value-of select="$ifTrue"/>
    } else {<xsl:text>
        </xsl:text><xsl:value-of select="$variable"/> = <xsl:value-of select="$ifFalse"/>
    }</xsl:when>
        <xsl:otherwise>
    <xsl:value-of select="$variable"/> = <xsl:value-of select="$oldExpression"/><xsl:text>
        </xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>


</xsl:stylesheet>