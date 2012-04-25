<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:meta="http://morphml.org/metadata/schema"
    xmlns:cml="http://morphml.org/channelml/schema">

<!--

    This file is used to convert ChannelML files to GENESIS tabchannel/tab2Dchannel/leakage based script files

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

<!-- Can be altered in this file to include/exclude lines printed during execution, for decoding purposes -->
<xsl:variable name="consoleOutput">no</xsl:variable>

<!-- The unit system (SI or Physiological) as used in the ChannelML file we're converting -->
<xsl:variable name="xmlFileUnitSystem"><xsl:value-of select="/cml:channelml/@units"/></xsl:variable>

<!-- The unit system (SI or Physiological) we wish to convert into (Note changing this value in this file
     will create a GENESIS script in different units) -->
<xsl:variable name="targetUnitSystem">Physiological Units</xsl:variable>

<!--Main template-->

<xsl:template match="/cml:channelml">
<xsl:text>// This is a GENESIS script file generated from a ChannelML v1.8.1 file
// The ChannelML file is mapped onto a tabchannel object

</xsl:text>
// Units of ChannelML file: <xsl:value-of select="$xmlFileUnitSystem"/>, units of GENESIS file generated: <xsl:value-of
select="$targetUnitSystem"/>

<xsl:if test="count(meta:notes) &gt; 0">

/*
    <xsl:value-of select="meta:notes"/>
*/
</xsl:if>


<!-- Only do the first channel --><xsl:choose><xsl:when test="count(cml:channel_type/cml:ks_gate) &gt; 0">
    *** Note: Kinetic scheme based ChannelML descriptions cannot be mapped on to GENESIS at the present time. ***
</xsl:when>
<xsl:when test="count(cml:channel_type/cml:current_voltage_relation/cml:integrate_and_fire) &gt; 0">
    *** Note: Integrate and Fire mechanisms cannot be mapped on to GENESIS at the present time. ***
</xsl:when>

<xsl:otherwise>
<xsl:apply-templates  select="cml:channel_type"/>
</xsl:otherwise>
</xsl:choose>

<!-- If there is a concentration mechanism present -->
<xsl:apply-templates  select="cml:ion_concentration"/>

<!-- Do a synapse if there -->
<xsl:apply-templates  select="cml:synapse_type"/>

</xsl:template>
<!--End Main template-->


<xsl:template match="cml:channel_type">
    
    <!-- Whether it is a passive channel-->
    <xsl:variable name="passiveChannel">
        <xsl:choose>
            <xsl:when test="count(//cml:gate) &gt; 0">no</xsl:when>
            <xsl:otherwise>yes</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    
    <!-- Whether there is a voltage and concentration dependence in the channel-->
    <xsl:variable name="voltConcDependence">
        <xsl:choose>
            <xsl:when test="count(//cml:voltage_conc_gate) &gt; 0">yes</xsl:when>
            <xsl:when test="count(//cml:conc_dependence) &gt; 0">yes</xsl:when>
            <xsl:otherwise>no</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <!-- A special case where there is only caconc dependence, no v dependence, and so a tab2dchannel
    doesn't need to be used-->
    <xsl:variable name="voltConcDependenceSimple">
        <xsl:choose>
            <xsl:when test="count(//cml:conc_dependence) = 0 or
                            contains(cml:current_voltage_relation/cml:gate[1]/cml:transition[1]/@expr, 'v') or
                            contains(cml:current_voltage_relation/cml:gate[1]/cml:transition[2]/@expr, 'v') or
                            count(cml:current_voltage_relation/cml:gate) &gt; 1">no</xsl:when>
            <xsl:otherwise>yes</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <!-- Whether there is a voltage and concentration dependence in the channel-->
    <xsl:variable name="postV1_7_3format">
        <xsl:choose>
            <xsl:when test="count(//cml:current_voltage_relation/@cond_law) &gt; 0">yes</xsl:when>
            <xsl:otherwise>no</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:if test="count(cml:parameters/cml:parameter) &gt; 0">
// NOTE: There are parameters in the ChannelML file, so there will be a seperate init of the table
extern init_<xsl:value-of select="@name"/><xsl:text>
        
    </xsl:text>

    </xsl:if>
function make_<xsl:value-of select="@name"/>
        <xsl:if test="count(meta:notes) &gt; 0">

        /*
            <xsl:value-of select="meta:notes"/><xsl:for-each select="meta:publication"><xsl:text>

            </xsl:text>Reference: <xsl:value-of select="meta:fullTitle"/>
            Pubmed: <xsl:value-of select="meta:pubmedRef"/></xsl:for-each>
        */
        </xsl:if>

        str chanpath = "/library/<xsl:value-of select="@name"/>"

        if ({exists {chanpath}})
            return
        end<xsl:text>
        </xsl:text>


        <xsl:variable name="ionname">
            <xsl:choose>
                <xsl:when test="count(cml:current_voltage_relation/cml:ohmic) &gt; 0"><xsl:value-of select="cml:current_voltage_relation/cml:ohmic/@ion"/></xsl:when>
                <xsl:when test="count(cml:current_voltage_relation/@ion) &gt; 0"><xsl:value-of select="cml:current_voltage_relation/@ion"/></xsl:when>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="erev">
            <xsl:choose>
                <xsl:when test="count(/cml:channelml/cml:ion[@name=$ionname]/@default_erev) &gt; 0"><xsl:value-of select="/cml:channelml/cml:ion[@name=$ionname]/@default_erev"/></xsl:when>
                <xsl:when test="count(cml:current_voltage_relation/@default_erev) &gt; 0"><xsl:value-of select="cml:current_voltage_relation/@default_erev"/></xsl:when>
            </xsl:choose>
        </xsl:variable>

        <xsl:choose>
            <xsl:when test="$passiveChannel = 'yes'">
        create leakage {chanpath}
            </xsl:when>
            <xsl:when test="$voltConcDependenceSimple = 'yes'">
        create tabchannel {chanpath}
            </xsl:when>
            <xsl:when test="$voltConcDependence = 'yes'">
        create tab2Dchannel {chanpath}
            </xsl:when>
            <xsl:otherwise>
        create tabchannel {chanpath}
            </xsl:otherwise>
        </xsl:choose>

        setfield {chanpath} \ 
            Ek              <xsl:call-template name="convert">
                                    <xsl:with-param name="value" select="$erev"/>
                                    <xsl:with-param name="quantity">Voltage</xsl:with-param>
                               </xsl:call-template> \
            Ik              0 <xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[1]) &gt; 0"> \
            Xpower          <xsl:value-of select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[1]/@power"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[2]) &gt; 0"> \
            Ypower          <xsl:value-of select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[2]/@power"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[3]) &gt; 0"> \
            Zpower          <xsl:value-of select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate[3]/@power"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:conc_factor) &gt; 0"> \
            Zpower          1
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:gate[1]) &gt; 0 and $voltConcDependenceSimple = 'no'"> \
            Xpower          <xsl:value-of select="cml:current_voltage_relation/cml:gate[1]/@instances"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:gate[2]) &gt; 0"> \
            Ypower          <xsl:value-of select="cml:current_voltage_relation/cml:gate[2]/@instances"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:gate[3]) &gt; 0"> \
            Zpower          <xsl:value-of select="cml:current_voltage_relation/cml:gate[3]/@instances"/>
            </xsl:if><xsl:if test="count(cml:current_voltage_relation/cml:conc_factor) &gt; 0 and $voltConcDependenceSimple = 'no'"> \
            Zpower          1
            </xsl:if><xsl:if test="$voltConcDependenceSimple = 'yes'"> \
            Zpower          <xsl:value-of select="cml:current_voltage_relation/cml:gate[1]/@instances"/>
            </xsl:if>
            <xsl:text>
        </xsl:text>
        <xsl:choose>
            <xsl:when test="$passiveChannel = 'yes' and $postV1_7_3format = 'no' and count(cml:current_voltage_relation/cml:ohmic/cml:conductance/*) = 0">
        setfield {chanpath} Gk <xsl:call-template name="convert">
                                    <xsl:with-param name="value" select="cml:current_voltage_relation/cml:ohmic/cml:conductance/@default_gmax"/>
                                    <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
                               </xsl:call-template><xsl:text>

        </xsl:text>
            </xsl:when>
            <xsl:when test="$passiveChannel = 'yes' and $postV1_7_3format = 'yes' and count(cml:current_voltage_relation/*) = 0">
        setfield {chanpath} Gk <xsl:call-template name="convert">
                                    <xsl:with-param name="value" select="cml:current_voltage_relation/@default_gmax"/>
                                    <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
                               </xsl:call-template><xsl:text>

        </xsl:text>
            </xsl:when>
            <xsl:when test="$postV1_7_3format = 'no'">
        setfield {chanpath} \
            Gbar <xsl:call-template name="convert">
                                    <xsl:with-param name="value" select="cml:current_voltage_relation/cml:ohmic/cml:conductance/@default_gmax"/>
                                    <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
                               </xsl:call-template> \
            Gk              0 <xsl:text>

        </xsl:text>
            </xsl:when>
            <xsl:otherwise>
        setfield {chanpath} \
            Gbar <xsl:call-template name="convert">
                                    <xsl:with-param name="value" select="cml:current_voltage_relation/@default_gmax"/>
                                    <xsl:with-param name="quantity">Conductance Density</xsl:with-param>
                               </xsl:call-template> \
            Gk              0 <xsl:text>

        </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        
        <xsl:if test="count(cml:parameters/cml:parameter) &gt; 0">
        // There are parameters in the ChannelML file, which may be changed after initialisation which could mean the tables 
        // will need to be updated. Seperating out the generation of the table values into init function.
        
        <xsl:for-each select="cml:parameters/cml:parameter">
        addfield {chanpath} <xsl:value-of select="@name"/>
        setfield {chanpath} <xsl:value-of select="@name"/>  <xsl:text> </xsl:text><xsl:value-of select="@value"/> // Note units of this will be determined by its usage in the generic functions
        </xsl:for-each>
        
        init_<xsl:value-of select="@name"/> {chanpath}  // Initialisation of the tables
        
end // End of main channel definition


// calling this function after changing the extra parameters/added fields will updated the table
function init_<xsl:value-of select="@name"/>(chanpath)

        str chanpath
        
        // Retrieving the param values as local variables
        <xsl:for-each select="cml:parameters/cml:parameter">
        float <xsl:value-of select="@name"/> = {getfield {chanpath} <xsl:value-of select="@name"/>}
        </xsl:for-each>
        
        </xsl:if>

        <xsl:if test="$passiveChannel = 'no'">
            
            <xsl:choose>
                <xsl:when test="count(cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:q10_settings) &gt; 0 or
                                count(cml:current_voltage_relation/cml:q10_settings) &gt; 0">
        // There is a Q10 factor which will alter the tau of the gates
            <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:q10_settings |
                                  cml:current_voltage_relation/cml:q10_settings">
                <xsl:choose>
                    <xsl:when test="count(@gate) &gt; 0">
                        <xsl:choose><xsl:when test="count(@q10_factor) &gt; 0">
        float temp_adj_<xsl:value-of select="@gate"/> = {pow <xsl:value-of select="@q10_factor"/> {(celsius - <xsl:value-of select="@experimental_temp"/>)/10}}
                        </xsl:when><xsl:when test="count(@fixed_q10) &gt; 0">
        float temp_adj_<xsl:value-of select="@gate"/> = <xsl:value-of select="@fixed_q10"/>
                        </xsl:when></xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:choose><xsl:when test="count(@q10_factor) &gt; 0">
                            <xsl:variable name="expression">{pow <xsl:value-of select="@q10_factor"/> {(celsius - <xsl:value-of select="@experimental_temp"/>)/10}}</xsl:variable>
                            <xsl:for-each select="../../cml:gate">             <!-- pre v1.7.3-->
        float temp_adj_<xsl:value-of select="cml:state/@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each><xsl:for-each select="../cml:gate"> <!-- post v1.7.3-->
        float temp_adj_<xsl:value-of select="@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                        </xsl:when><xsl:when test="count(@fixed_q10) &gt; 0">
                            <xsl:variable name="expression"><xsl:value-of select="@fixed_q10"/></xsl:variable>
                            <xsl:for-each select="../../cml:gate">    <!-- pre v1.7.3-->
        float temp_adj_<xsl:value-of select="cml:state/@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                            <xsl:for-each select="../cml:gate">       <!-- post v1.7.3-->
        float temp_adj_<xsl:value-of select="@name"/> = <xsl:value-of select="$expression"/>
                            </xsl:for-each>
                        </xsl:when></xsl:choose>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
        // No Q10 temperature adjustment found
    <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate">    float temp_adj_<xsl:value-of 
    select="cml:state/@name"/> = 1
    </xsl:for-each>
    <xsl:for-each select="cml:current_voltage_relation/cml:gate">    float temp_adj_<xsl:value-of 
    select="@name"/> = 1
    </xsl:for-each>
                </xsl:otherwise>
            </xsl:choose>
            
            

         <xsl:variable name="max_v">
            <xsl:choose>
                <xsl:when test="count(cml:impl_prefs/cml:table_settings) = 0"><xsl:choose>
                            <xsl:when test="$targetUnitSystem  = 'Physiological Units'">100</xsl:when>
                            <xsl:otherwise>0.1</xsl:otherwise>
                        </xsl:choose></xsl:when>
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
                <xsl:when test="count(cml:impl_prefs/cml:table_settings) = 0"><xsl:choose>
                            <xsl:when test="$targetUnitSystem  = 'Physiological Units'">-100</xsl:when>
                            <xsl:otherwise>-0.1</xsl:otherwise>
                        </xsl:choose></xsl:when>
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

        float tab_divs = <xsl:value-of select="$table_divisions"/>


            <xsl:if test="$voltConcDependenceSimple = 'no'">
        float v_min = <xsl:value-of select="$min_v"/>

        float v_max = <xsl:value-of select="$max_v"/>

        float v, dv, i
            </xsl:if>
        </xsl:if>

        <xsl:for-each select='cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate |
                              cml:current_voltage_relation/cml:gate'>

            <xsl:variable name='gateName'><xsl:value-of select="cml:state/@name"/><xsl:value-of select="@name"/></xsl:variable> <!-- Will be one or the other -->
            <xsl:variable name='gateRef'>
                <xsl:if test='position()=1'>X</xsl:if>
                <xsl:if test='position()=2'>Y</xsl:if>
                <xsl:if test='position()=3'>Z</xsl:if>
            </xsl:variable>

            <xsl:if test="$voltConcDependenceSimple = 'no'">
        // Creating table for gate <xsl:value-of select="$gateName"/>, using name <xsl:value-of select="$gateRef"/> for it here

        float dv = ({v_max} - {v_min})/{tab_divs}
            </xsl:if>

        <xsl:for-each select="../../../../cml:hh_gate[@state=$gateName] | 
                              ../cml:gate[@name=$gateName]">

            <xsl:choose>
                <xsl:when test="$voltConcDependence = 'yes'">
                    <xsl:for-each select="cml:transition/cml:voltage_conc_gate/cml:conc_dependence | ../cml:conc_dependence">

        // Channel is dependent on concentration of: <xsl:value-of select="@name"/>, rate equations will involve variable: <xsl:value-of select="@variable_name"/>
        float c
        float conc_min = <xsl:call-template name="convert">
                                <xsl:with-param name="value"><xsl:value-of select="@min_conc"/></xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                        </xsl:call-template>
        float conc_max = <xsl:call-template name="convert">
                                <xsl:with-param name="value"><xsl:value-of select="@max_conc"/></xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                        </xsl:call-template>

        float dc = ({conc_max} - {conc_min})/{tab_divs}

        float <xsl:value-of select="@variable_name"/> = {conc_min}

        <!-- Impl here may not be generic enough for all cases -->

            <xsl:if test="$voltConcDependenceSimple = 'no'">
        // Setting up the volt/conc dependent 2D table
        setfield {chanpath}  <xsl:value-of select="$gateRef"/>index {VOLT_C1_INDEX} // assumes all gates are volt/conc dep
            </xsl:if>

            <xsl:if test="$voltConcDependenceSimple = 'no'">
        call {chanpath} TABCREATE <xsl:value-of select="$gateRef"/> {tab_divs} {v_min} {v_max} {tab_divs} {conc_min} {conc_max}
            </xsl:if>

            <xsl:if test="$voltConcDependenceSimple = 'yes'">
        call {chanpath} TABCREATE Z {tab_divs} {conc_min} {conc_max}
            </xsl:if>

        for (c = 0; c &lt;= ({tab_divs}); c = c + 1)
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
        call {chanpath} TABCREATE <xsl:value-of select="$gateRef"/> {tab_divs} {v_min} {v_max}
                </xsl:otherwise>
            </xsl:choose>

            <xsl:if test="$voltConcDependenceSimple = 'no'">
        v = {v_min}

            <xsl:for-each select="../cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:rate_adjustments/cml:offset |
                                  ../cml:offset">  <!-- pre | post v1.7.3-->
        // There is a voltage offset of <xsl:value-of select="@value"/>. This will shift the dependency of the rate equations
        v = v - <xsl:call-template name="convert">
                    <xsl:with-param name="value" select="@value"/>
                    <xsl:with-param name="quantity">Voltage</xsl:with-param>
                </xsl:call-template><xsl:text>
            </xsl:text>
            </xsl:for-each>

        for (i = 0; i &lt;= ({tab_divs}); i = i + 1)
            </xsl:if>
        <xsl:if test="$postV1_7_3format = 'no'">          
            <xsl:for-each select='cml:transition/*/*'>
                <xsl:if test="name()!='conc_dependence' and name()!='initialisation'">
            // Looking at rate: <xsl:value-of select="name()"/><xsl:text>
                </xsl:text>
            float <xsl:value-of select="name()"/>    <xsl:text>
                </xsl:text>

                <xsl:choose>
                    <xsl:when  test="count(cml:parameterised_hh) &gt; 0">
            float A, B, k, V0
                        <xsl:call-template name="generateOldEquation">
                            <xsl:with-param name="name"><xsl:value-of select="name()"/></xsl:with-param>
                            <xsl:with-param name="functionForm" select="cml:parameterised_hh/@type" />
                            <xsl:with-param name="expression"   select="cml:parameterised_hh/@expr" />
                            <xsl:with-param name="A_cml" select="cml:parameterised_hh/cml:parameter[@name='A']/@value"/>
                            <xsl:with-param name="k_cml" select="cml:parameterised_hh/cml:parameter[@name='k']/@value"/>
                            <xsl:with-param name="d_cml" select="cml:parameterised_hh/cml:parameter[@name='d']/@value"/>
                        </xsl:call-template>
                    </xsl:when>
                    <xsl:when test="count(cml:generic_equation_hh) &gt; 0 or count(cml:generic) &gt; 0">
                    <xsl:variable name="expr"><xsl:value-of select="cml:generic_equation_hh/@expr" /><xsl:value-of select="cml:generic/@expr" /></xsl:variable> <!--Will be one or the other-->
            // Found a generic form of rate equation for <xsl:value-of select="name()"/>, using expression: <xsl:value-of select="$expr" />
            // Will translate this for GENESIS compatibility...<xsl:text>
                    </xsl:text>
                    <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
            // Equation (and all ChannelML file values) in <xsl:value-of select="$xmlFileUnitSystem"
            /> but this script in <xsl:value-of select="$targetUnitSystem" /><xsl:text>
            </xsl:text>
            v = v * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
                    </xsl:call-template> // temporarily set v to units of equation...<xsl:text>
            </xsl:text>
                        <xsl:if test="(name()='tau' or name()='inf') and
                                      (contains(string($expr), 'alpha') or
                                      contains(string($expr), 'beta'))">
            // Equation depends on alpha/beta, so converting them too...
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template>
            beta = beta * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template> <xsl:text>
            </xsl:text>
                        </xsl:if>
                        <xsl:if test="name()='beta' and
                                      contains(string($expr), 'alpha')">
            // Equation depends on alpha, so converting it...
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template> <xsl:text>
            </xsl:text>
                        </xsl:if>

                        <xsl:if test="count(../cml:conc_dependence) &gt; 0">
           // Equation depends on concentration, so converting that too... <xsl:text>
            </xsl:text>
            <xsl:value-of select="../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvConcentration</xsl:with-param>
                            </xsl:call-template> <xsl:text>

            </xsl:text>
                        </xsl:if>
                    </xsl:if>
                    <xsl:variable name="newExpression">
                        <xsl:call-template name="formatExpression">
                            <xsl:with-param name="variable">
                                <xsl:value-of select="name()"/>
                            </xsl:with-param>
                            <xsl:with-param name="oldExpression">
                                <xsl:value-of select="$expr" />
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
            <xsl:value-of select="$newExpression" /><xsl:text>
            </xsl:text>
                    <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
            v = v * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Voltage</xsl:with-param>
                    </xsl:call-template> // reset v<xsl:text>
            </xsl:text>
                    <xsl:if test="(name()='tau' or name()='inf') and
                                      (contains(string($expr), 'alpha') or
                                      contains(string($expr), 'beta'))">
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting alpha
            beta = beta * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting beta
                        </xsl:if>
                        
                    <xsl:if test="name()='beta' and
                                      contains(string($expr), 'alpha')">
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting alpha
                        </xsl:if>

                        <xsl:if test="count(../cml:conc_dependence) &gt; 0">
            <xsl:value-of select="../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                            </xsl:call-template> // resetting ca_conc <xsl:text>

            </xsl:text>
                        </xsl:if>
                    </xsl:if>




                    <xsl:if test="(name()='alpha' or name()='beta')
                                   and (string($xmlFileUnitSystem) != string($targetUnitSystem))">
            // Set correct units of <xsl:value-of select="name()"/><xsl:text>
            </xsl:text>
            <xsl:value-of select="name()"/> = <xsl:value-of select="name()"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">InvTime</xsl:with-param>
                        </xsl:call-template><xsl:text>

            </xsl:text>
                    </xsl:if>

                    <xsl:if test="name()='tau' and (string($xmlFileUnitSystem) != string($targetUnitSystem))">
            // Set correct units of <xsl:value-of select="name()"/><xsl:text>
            </xsl:text>
            <xsl:value-of select="name()"/> = <xsl:value-of select="name()"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">Time</xsl:with-param>
                        </xsl:call-template>
                    </xsl:if>



                    </xsl:when>
                    <xsl:otherwise>
            ? ERROR: Unrecognised form of the rate equation for <xsl:value-of select="name()"/>...

                    </xsl:otherwise>
                </xsl:choose>
                </xsl:if>
            </xsl:for-each> <!-- <xsl:for-each select='cml:transition/*/* ... etc>-->

            <xsl:variable name='tableEntry'>
                <xsl:choose>
                    <xsl:when test="count(cml:transition/cml:voltage_gate) &gt; 0">table[{i}]</xsl:when>
                    <xsl:when test="count(cml:transition/cml:voltage_conc_gate) &gt; 0">table[{i}][{c}]</xsl:when>
                </xsl:choose>
            </xsl:variable>

            <!-- Working out the conversion of alpha and beta to tau & inf-->
            <xsl:choose>
                <xsl:when test="count(cml:transition/cml:voltage_gate/cml:alpha | cml:transition/cml:voltage_conc_gate/cml:alpha)=1 and
                                count(cml:transition/cml:voltage_gate/cml:beta | cml:transition/cml:voltage_conc_gate/cml:beta)=1 and
                                count(cml:transition/cml:voltage_gate/cml:tau | cml:transition/cml:voltage_conc_gate/cml:tau)=0 and
                                count(cml:transition/cml:voltage_gate/cml:inf | cml:transition/cml:voltage_conc_gate/cml:inf)=0">

            // Using the alpha and beta expressions to populate the tables

            float tau = 1/(temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta))
            <xsl:if test="$consoleOutput='yes'">echo "Tab <xsl:value-of select="$gateRef"/>: v: "{v} ", a: "{alpha} ", b: "{beta} ", tau: "{tau}
                <xsl:if test="count(cml:transition/cml:voltage_conc_gate) &gt; 0">
            echo "Tab <xsl:value-of select="$gateRef"/>: conc: " {<xsl:value-of select="cml:transition/cml:voltage_conc_gate/cml:conc_dependence/@variable_name"/>}
                </xsl:if>
            </xsl:if>
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * alpha}
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta)}
                </xsl:when>
                <xsl:otherwise>

            // Evaluating the tau and inf expressions

                    <xsl:choose>
                        <xsl:when test="count(cml:transition/cml:voltage_gate/cml:tau | cml:transition/cml:voltage_conc_gate/cml:tau)=0">
            float tau = 1/(temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta))
                        </xsl:when>
                        <xsl:otherwise>
            tau = tau/temp_adj_<xsl:value-of select="$gateName"/>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:if test="count(cml:transition/cml:voltage_gate/cml:inf | cml:transition/cml:voltage_conc_gate/cml:inf)=0">
            float inf = alpha/(alpha + beta)
                    </xsl:if>

            <xsl:if test="$consoleOutput='yes'">echo "Tab <xsl:value-of select="$gateRef"/>: v: "{v} ", tau: "{tau} ", inf: "{inf}
                <xsl:if test="count(cml:transition/cml:voltage_conc_gate) &gt; 0">
                echo "Tab <xsl:value-of select="$gateRef"/>: conc: " {<xsl:value-of select="cml:transition/cml:voltage_conc_gate/cml:conc_dependence/@variable_name"/>}
                </xsl:if>
            </xsl:if>
<!--
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {tau}

            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {inf}-->
            
            // Working out the "real" alpha and beta expressions from the tau and inf
            <xsl:if test="count(cml:transition/cml:voltage_gate/cml:alpha | cml:transition/cml:voltage_conc_gate/cml:alpha)=0">
            float alpha</xsl:if>
            <xsl:if test="count(cml:transition/cml:voltage_gate/cml:beta | cml:transition/cml:voltage_conc_gate/cml:beta)=0">
            float beta</xsl:if>
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {alpha}
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {alpha + beta}

                </xsl:otherwise>
            </xsl:choose>
        </xsl:if>
        <xsl:if test="$postV1_7_3format = 'yes'">          
            <xsl:for-each select='*'>
                <xsl:if test="name()!='conc_dependence' and 
                              name()!='initialisation' and 
                              name()!='closed_state' and 
                              name()!='open_state'">
            // Looking at rate: <xsl:value-of select="@name"/><xsl:text>
                </xsl:text>
            float <xsl:value-of select="@name"/>    <xsl:text>
                </xsl:text>

                <xsl:choose>
                    <xsl:when  test="@expr_form='exp_linear' or 
                                     @expr_form='exponential' or 
                                     @expr_form='sigmoid'">
            float A, B, Vhalf
                        <xsl:call-template name="generateNewEquation">
                            <xsl:with-param name="name"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="functionForm" select="@expr_form" />
                            <xsl:with-param name="rate" select="@rate"/>
                            <xsl:with-param name="scale" select="@scale"/>
                            <xsl:with-param name="midpoint" select="@midpoint"/>
                        </xsl:call-template>
                    </xsl:when>
                    <xsl:when test="@expr_form='generic'">
                        
            // Found a generic form of rate equation for <xsl:value-of select="@name"/>, using expression: <xsl:value-of select="@expr" />
            // Will translate this for GENESIS compatibility...<xsl:text>
                    </xsl:text>
                    <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
            // Equation (and all ChannelML file values) in <xsl:value-of select="$xmlFileUnitSystem"
            /> but this script in <xsl:value-of select="$targetUnitSystem" /><xsl:text>
            </xsl:text>
            v = v * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
                    </xsl:call-template> // temporarily set v to units of equation...<xsl:text>
            </xsl:text>
                        <xsl:if test="(@name='tau' or @name='inf') and
                                      (contains(string(@expr), 'alpha') or
                                      contains(string(@expr), 'beta'))">
            // Equation depends on alpha/beta, so converting them too...
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template>
            beta = beta * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template> <xsl:text>
            </xsl:text>
                        </xsl:if>
                        <xsl:if test="@name='beta' and
                                      contains(string(@expr), 'alpha')">
            // Equation depends on alpha, so converting it...
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Time</xsl:with-param>
                            </xsl:call-template> <xsl:text>
            </xsl:text>
                        </xsl:if>

                        <xsl:if test="count(../../cml:conc_dependence) &gt; 0">
           // Equation depends on concentration, so converting that too... <xsl:text>
            </xsl:text>
            <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvConcentration</xsl:with-param>
                            </xsl:call-template> <xsl:text>

            </xsl:text>
                        </xsl:if>
                    </xsl:if>
                    <xsl:variable name="newExpression">
                        <xsl:call-template name="formatExpression">
                            <xsl:with-param name="variable">
                                <xsl:value-of select="@name"/>
                            </xsl:with-param>
                            <xsl:with-param name="oldExpression">
                                <xsl:value-of select="@expr" />
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
            <xsl:value-of select="$newExpression" /><xsl:text>
            </xsl:text>
                    <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
            v = v * <xsl:call-template name="convert">
                        <xsl:with-param name="value">1</xsl:with-param>
                        <xsl:with-param name="quantity">Voltage</xsl:with-param>
                    </xsl:call-template> // reset v<xsl:text>
            </xsl:text>
                    <xsl:if test="(@name='tau' or @name='inf') and
                                      (contains(string(@expr), 'alpha') or
                                      contains(string(@expr), 'beta'))">
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting alpha
            beta = beta * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting beta
                        </xsl:if>
                        
                    <xsl:if test="@name='beta' and
                                      contains(string(@expr), 'alpha')">
            alpha = alpha * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvTime</xsl:with-param>
                            </xsl:call-template>  // resetting alpha
                        </xsl:if>

                        <xsl:if test="count(../../cml:conc_dependence) &gt; 0">
            <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> = <xsl:value-of select="../../cml:conc_dependence/@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                            </xsl:call-template> // resetting ca_conc <xsl:text>

            </xsl:text>
                        </xsl:if>
                    </xsl:if>




                    <xsl:if test="(@name='alpha' or @name='beta')
                                   and (string($xmlFileUnitSystem) != string($targetUnitSystem))">
            // Set correct units of <xsl:value-of select="@name"/><xsl:text>
            </xsl:text>
            <xsl:value-of select="@name"/> = <xsl:value-of select="@name"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">InvTime</xsl:with-param>
                        </xsl:call-template><xsl:text>

            </xsl:text>
                    </xsl:if>

                    <xsl:if test="@name='tau' and (string($xmlFileUnitSystem) != string($targetUnitSystem))">
            // Set correct units of <xsl:value-of select="@name"/><xsl:text>
            </xsl:text>
            <xsl:value-of select="@name"/> = <xsl:value-of select="@name"/> * <xsl:call-template name="convert">
                            <xsl:with-param name="value">1</xsl:with-param>
                            <xsl:with-param name="quantity">Time</xsl:with-param>
                        </xsl:call-template>
                    </xsl:if>



                    </xsl:when>
                    <xsl:otherwise>
            ? ERROR: Unrecognised form of the rate equation for <xsl:value-of select="@name"/>...

                    </xsl:otherwise>
                </xsl:choose>
                </xsl:if>
            </xsl:for-each> <!-- <xsl:for-each select='cml:transition/*/* ... etc>-->

            <xsl:variable name='tableEntry'>
                <xsl:choose>
                    <xsl:when test="$voltConcDependenceSimple = 'yes'">table[{c}]</xsl:when>
                    <xsl:when test="$voltConcDependence = 'no'">table[{i}]</xsl:when>
                    <xsl:when test="$voltConcDependence = 'yes'">table[{i}][{c}]</xsl:when>
                </xsl:choose>
            </xsl:variable>

            <!-- Working out the conversion of alpha and beta to tau & inf-->
            <xsl:choose>
                <xsl:when test="count(cml:transition[@name='alpha']) = 1 and
                                count(cml:transition[@name='beta']) = 1 and
                                count(cml:time_course) = 0 and
                                count(cml:steady_state) = 0">

            // Using the alpha and beta expressions to populate the tables

            float tau = 1/(temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta))
            <xsl:if test="$consoleOutput='yes'">echo "Tab <xsl:value-of select="$gateRef"/>: v: "{v} ", a: "{alpha} ", b: "{beta} ", tau: "{tau}
                <xsl:if test="count(../../cml:conc_dependence) &gt; 0">
            echo "Tab <xsl:value-of select="$gateRef"/>: conc: " {<xsl:value-of select="../../cml:conc_dependence/@variable_name"/>}
                </xsl:if>
            </xsl:if>

                <xsl:choose>
                    <xsl:when test="$voltConcDependenceSimple = 'no'">
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * alpha}
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta)}
                    </xsl:when>
                    <xsl:otherwise>
            setfield {chanpath} Z_A-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * alpha}
            setfield {chanpath} Z_B-><xsl:value-of select="$tableEntry"/> {temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta)}
                    </xsl:otherwise>
                </xsl:choose>

                </xsl:when>
                <xsl:otherwise>

            // Evaluating the tau and inf expressions

                    <xsl:choose>
                        <xsl:when test="count(cml:time_course)=0">
            float tau = 1/(temp_adj_<xsl:value-of select="$gateName"/> * (alpha + beta))
                        </xsl:when>
                        <xsl:otherwise>
            tau = tau/temp_adj_<xsl:value-of select="$gateName"/>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:if test="count(cml:steady_state)=0">
            float inf = alpha/(alpha + beta)
                    </xsl:if>

            <xsl:if test="$consoleOutput='yes'">echo "Tab <xsl:value-of select="$gateRef"/>: v: "{v} ", tau: "{tau} ", inf: "{inf}
                <xsl:if test="count(../../cml:conc_dependence) &gt; 0">
                echo "Tab <xsl:value-of select="$gateRef"/>: conc: " {<xsl:value-of select="../../cml:conc_dependence/@variable_name"/>}
                </xsl:if>
            </xsl:if>
<!--
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {tau}

            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {inf}-->
            
            // Working out the "real" alpha and beta expressions from the tau and inf
            <xsl:if test="count(cml:transition[@name='alpha']) = 0">
            float alpha</xsl:if>
            <xsl:if test="count(cml:transition[@name='beta']) = 0">
            float beta</xsl:if>
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_A-><xsl:value-of select="$tableEntry"/> {alpha}
            setfield {chanpath} <xsl:value-of select="$gateRef"/>_B-><xsl:value-of select="$tableEntry"/> {alpha + beta}

                </xsl:otherwise>
            </xsl:choose>
        </xsl:if>

            <xsl:if test="$voltConcDependenceSimple = 'no'">
            v = v + dv

        end // end of for (i = 0; i &lt;= ({tab_divs}); i = i + 1)
            </xsl:if>

        <xsl:if test="$voltConcDependence = 'yes'">
            <xsl:choose>
                <xsl:when test="$postV1_7_3format = 'yes'">
        <xsl:value-of select="../cml:conc_dependence/@variable_name"/> = <xsl:value-of
                select="../cml:conc_dependence/@variable_name"/> + dc
                </xsl:when>
                <xsl:otherwise>
        <xsl:value-of select="cml:transition/cml:voltage_conc_gate/cml:conc_dependence/@variable_name"/> = <xsl:value-of
                select="cml:transition/cml:voltage_conc_gate/cml:conc_dependence/@variable_name"/> + dc
                </xsl:otherwise>
            </xsl:choose>
                
        end // end of for (c = 0; c &lt;= ({tab_divs}); c = c + 1)
                </xsl:if>




                <xsl:choose>
                    <xsl:when test="$voltConcDependenceSimple = 'no'">
        setfield {chanpath} <xsl:value-of select="$gateRef"/>_A->calc_mode 1 <xsl:value-of select="$gateRef"/>_B->calc_mode 1
                    </xsl:when>
                    <xsl:otherwise>
        setfield {chanpath} Z_conc 1
        setfield {chanpath} Z_A->calc_mode 1 Z_B->calc_mode 1
                    </xsl:otherwise>
                </xsl:choose>

        </xsl:for-each> <!-- <xsl:for-each select="cml:hh_gate/[@state=$gateName]"> -->

        </xsl:for-each> <!--<xsl:for-each select='cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:gate'>-->
        
        <xsl:for-each select="cml:current_voltage_relation/cml:ohmic/cml:conductance/cml:conc_factor | cml:current_voltage_relation/cml:conc_factor">
        // Adding voltage independent concentration term
        
        
        float conc_min = <xsl:call-template name="convert">
                                <xsl:with-param name="value"><xsl:value-of select="@min_conc"/></xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                        </xsl:call-template>
        float conc_max = <xsl:call-template name="convert">
                                <xsl:with-param name="value"><xsl:value-of select="@max_conc"/></xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                        </xsl:call-template>

        float dc = ({conc_max} - {conc_min})/{tab_divs}

        float <xsl:value-of select="@variable_name"/> = {conc_min}
        
        call {chanpath} TABCREATE  Z {tab_divs} {conc_min} {conc_max}
        
        float const_state

        for (i = 0; i &lt;= ({tab_divs}); i = i + 1)
        
            
            <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
                
            // Equation is in different set of units...
            <xsl:value-of select="@variable_name"/> = <xsl:value-of select="@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">InvConcentration</xsl:with-param>
                            </xsl:call-template> <xsl:text>

            </xsl:text>
                        </xsl:if>
            <xsl:variable name="newExpression">
                        <xsl:call-template name="formatExpression">
                            <xsl:with-param name="variable">const_state</xsl:with-param>
                            <xsl:with-param name="oldExpression">
                                <xsl:value-of select="@expr" />
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
            <xsl:value-of select="$newExpression" />
            <xsl:if test="string($xmlFileUnitSystem) != string($targetUnitSystem)">
                
            // Converting back...
            <xsl:value-of select="@variable_name"/> = <xsl:value-of select="@variable_name"/> * <xsl:call-template name="convert">
                                <xsl:with-param name="value">1</xsl:with-param>
                                <xsl:with-param name="quantity">Concentration</xsl:with-param>
                            </xsl:call-template> <xsl:text>

            </xsl:text>
                        </xsl:if>
          
            
            setfield {chanpath} Z_A->table[{i}] {0}
            setfield {chanpath} Z_B->table[{i}] {const_state}
            
            
            <xsl:value-of select="@variable_name"/>= <xsl:value-of select="@variable_name"/> + dc
            
        end
             
        tweaktau {chanpath} Z
        </xsl:for-each>


end

</xsl:template>
<!--End Main template-->




<xsl:template match="cml:ion_concentration">

        <xsl:if test="count(cml:decaying_pool_model/cml:ceiling) &gt; 0 or count(cml:decaying_pool_model/@ceiling) &gt; 0">
            
function __catchCeiling__(action)

    call . PROCESS -parent  // Carry out all normal actions 

    float caval = {getfield Ca}
    float cabase = {getfield Ca_base}
    float ceil = {getfield ceiling}

    if (caval > ceil)
        setfield Ca {ceil}
        setfield C {ceil - cabase}
    end 

end
        </xsl:if>
        
function make_<xsl:value-of select="@name"/>
        <xsl:if test="count(meta:notes) &gt; 0">

        /*
            <xsl:value-of select="meta:notes"/>
        */
        </xsl:if>

        str chanpath = "/library/<xsl:value-of select="@name"/>"

        if ({exists {chanpath}})
            return
        end<xsl:text>
        </xsl:text>

        <xsl:variable name="ionname"><xsl:value-of select="cml:current_voltage_relation/cml:ohmic/@ion"/></xsl:variable>

        create Ca_concen {chanpath}

        <xsl:if test="count(cml:decaying_pool_model) &gt; 0">
            
            <xsl:variable name="tau_val">
                <xsl:choose>
                  <xsl:when test="count(cml:decaying_pool_model/cml:decay_constant) &gt; 0 or count(cml:decaying_pool_model/@decay_constant) &gt; 0">
                       <xsl:call-template name="convert">
                            <xsl:with-param name="value">
                                <xsl:value-of select="cml:decaying_pool_model/cml:decay_constant"/><xsl:value-of select="cml:decaying_pool_model/@decay_constant"/> <!-- Either element or attr will be present...-->
                            </xsl:with-param>
                            <xsl:with-param name="quantity">Time</xsl:with-param>
                       </xsl:call-template>
                   </xsl:when>
                  <xsl:when test="count(cml:decaying_pool_model/cml:inv_decay_constant) &gt; 0 or count(cml:decaying_pool_model/@inv_decay_constant) &gt; 0">{ 1.0 / <xsl:call-template name="convert">
                            <xsl:with-param name="value">
                                <xsl:value-of select="cml:decaying_pool_model/cml:inv_decay_constant"/><xsl:value-of select="cml:decaying_pool_model/@inv_decay_constant"/> <!-- Either element or attr will be present...-->
                            </xsl:with-param>
                            <xsl:with-param name="quantity">InvTime</xsl:with-param>
                       </xsl:call-template> }  </xsl:when>
                </xsl:choose>
            </xsl:variable>
                

        // Setting params for a decaying_pool_model

        setfield {chanpath} \
            tau                   <xsl:value-of select="$tau_val"/>  \
            Ca_base               <xsl:call-template name="convert">
                                      <xsl:with-param name="value">
                                          <xsl:value-of select="cml:decaying_pool_model/cml:resting_conc"/><xsl:value-of select="cml:decaying_pool_model/@resting_conc"/> <!-- Either element or attr will be present...-->
                                      </xsl:with-param>
                                    <xsl:with-param name="quantity">Concentration</xsl:with-param>
                               </xsl:call-template>
        
        
        addfield {chanpath} beta -description "Inverse of tau, needed as this is parameter used in some implementations. If beta > 0, this will be used in preference to tau"
        setfield {chanpath} beta -1  

            <xsl:if test="count(cml:decaying_pool_model/cml:pool_volume_info) &gt; 0">

        setfield {chanpath} \
            thick               <xsl:call-template name="convert">
                                    <xsl:with-param name="value">
                                        <xsl:value-of select="cml:decaying_pool_model/cml:pool_volume_info/cml:shell_thickness"/><xsl:value-of select="cml:decaying_pool_model/cml:pool_volume_info/@shell_thickness"/> <!-- Either element or attr will be present...-->
                                    </xsl:with-param>
                                    <xsl:with-param name="quantity">Length</xsl:with-param>
                               </xsl:call-template>
            </xsl:if>
        
        
            <xsl:if test="count(cml:decaying_pool_model/cml:ceiling) &gt; 0 or count(cml:decaying_pool_model/@ceiling) &gt; 0">
            
        addfield {chanpath} ceiling -description "Maximum concentration pool will be allowed reach"
        setfield {chanpath} ceiling <xsl:call-template name="convert">
                                    <xsl:with-param name="value">
                                        <xsl:value-of select="cml:decaying_pool_model/cml:ceiling"/><xsl:value-of select="cml:decaying_pool_model/@ceiling"/> <!-- Either element or attr will be present...-->
                                    </xsl:with-param>
                                    <xsl:with-param name="quantity">Concentration</xsl:with-param>
                               </xsl:call-template>
                               
        addaction {chanpath} PROCESS __catchCeiling__
            </xsl:if>
            
        
        </xsl:if> 
end

function init_<xsl:value-of select="@name"/>(chanpath)

    float curr_beta = {getfield {chanpath} beta}
    if (curr_beta > 0)
        
        echo "Using the value of beta " {curr_beta} " in place of tau"
        setfield {chanpath} tau {1 / {curr_beta}}
    else
        echo "Keeping existing tau: " {getfield {chanpath} tau} " not beta: " {curr_beta}
    end
    

end

</xsl:template>




<xsl:template match="cml:synapse_type">

<xsl:choose>
    <xsl:when test="count(cml:electrical_syn)>0">
        
function connectGapJunction_<xsl:value-of select="@name"/>(compartmentA, compartmentB, weight)
   
    // Note: implementation based on suggestion of Reinoud Maex
    
    str compartmentA
    str compartmentB
    float conductance = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:electrical_syn/@conductance"/></xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template>

    str diffampname = {strcat "diffamp_" {rand 0 99999999}}  // to ensure a different diffamp name for each gap junc on this comp

    create diffamp {compartmentA}/{diffampname}

    addmsg {compartmentA} {compartmentA}/{diffampname} PLUS Vm
    addmsg {compartmentB} {compartmentA}/{diffampname} MINUS Vm

    setfield {compartmentA}/{diffampname} gain {conductance * weight}
    setfield {compartmentA}/{diffampname}  saturation 10e8

    addmsg {compartmentA}/{diffampname} {compartmentB} INJECT output


    create diffamp {compartmentB}/{diffampname}

    addmsg {compartmentB} {compartmentB}/{diffampname} PLUS Vm
    addmsg {compartmentA} {compartmentB}/{diffampname} MINUS Vm

    setfield {compartmentB}/{diffampname} gain {conductance * weight}
    setfield {compartmentB}/{diffampname}  saturation 10e8

    addmsg {compartmentB}/{diffampname} {compartmentA} INJECT output
    
end

    </xsl:when>
    <xsl:otherwise>
function makechannel_<xsl:value-of select="@name"/>(compartment, name)
        <xsl:if test="count(meta:notes) &gt; 0">
        /*
            <xsl:value-of select="meta:notes"/>
        */
        </xsl:if>
        str compartment
        str name

        if (!({exists {compartment}/{name}}))

            create      synchan               {compartment}/{name}
<xsl:if test="count(cml:doub_exp_syn)>0">
            setfield    ^ \
                    Ek                      <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:doub_exp_syn/@reversal_potential"/></xsl:with-param>
              <xsl:with-param name="quantity">Voltage</xsl:with-param></xsl:call-template> \
                    tau1                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:doub_exp_syn/@decay_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> \
                    tau2                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:doub_exp_syn/@rise_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> \
                    gmax                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:doub_exp_syn/@max_conductance"/></xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template>

            float tau2 = {getfield {compartment}/{name} tau2}
            
            if (tau2 == 0)  //  Single exponential synapse
                setfield {compartment}/{name} tau2 1e-9  
            end
            
            addmsg   {compartment}/{name}   {compartment} CHANNEL Gk Ek
            addmsg   {compartment}   {compartment}/{name} VOLTAGE Vm
</xsl:if>

<xsl:if test="count(cml:blocking_syn)>0">
            setfield    ^ \
                    Ek                      <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/@reversal_potential"/></xsl:with-param>
              <xsl:with-param name="quantity">Voltage</xsl:with-param></xsl:call-template> \
                    tau1                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/@decay_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> \
                    tau2                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/@rise_time"/></xsl:with-param>
              <xsl:with-param name="quantity">Time</xsl:with-param></xsl:call-template> \
                    gmax                    <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/@max_conductance"/></xsl:with-param>
              <xsl:with-param name="quantity">Conductance</xsl:with-param></xsl:call-template>
              
            float tau1 = {getfield {compartment}/{name} tau1}
            if (tau1 == 0)
                setfield {compartment}/{name} tau1 1e-9
            end
            
            addmsg   {compartment}   {compartment}/{name} VOLTAGE Vm

            if (! {exists {compartment}/{name}/Mg_BLOCK})

                float CMg = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/cml:block/@conc"/></xsl:with-param>
              <xsl:with-param name="quantity">Concentration</xsl:with-param></xsl:call-template>

                float eta = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/cml:block/@eta"/></xsl:with-param>
              <xsl:with-param name="quantity">InvConcentration</xsl:with-param></xsl:call-template>

                float gamma = <xsl:call-template name="convert">
              <xsl:with-param name="value"><xsl:value-of select="cml:blocking_syn/cml:block/@gamma"/></xsl:with-param>
              <xsl:with-param name="quantity">InvVoltage</xsl:with-param></xsl:call-template>

                create Mg_block {compartment}/{name}/Mg_BLOCK

                setfield {compartment}/{name}/Mg_BLOCK \
                    CMg {CMg}  \
                    KMg_A {1/eta} \
                    KMg_B {1.0/gamma}

                addmsg  {compartment}/{name}             {compartment}/{name}/Mg_BLOCK   CHANNEL    Gk Ek
                addmsg  {compartment}/{name}/Mg_BLOCK    {compartment}                   CHANNEL    Gk Ek
                addmsg  {compartment}                    {compartment}/{name}/Mg_BLOCK   VOLTAGE    Vm
            end

</xsl:if>

        end

end
    </xsl:otherwise>
</xsl:choose>

</xsl:template>




<!-- Function to return 1 for exponential, 2 for sigmoid, 3 for linoid-->
<xsl:template name="getFunctionForm">
    <xsl:param name="stringFunctionName"/>
    <xsl:choose>
        <xsl:when test="$stringFunctionName = 'exponential'">1</xsl:when>
        <xsl:when test="$stringFunctionName = 'sigmoid'">2</xsl:when>
        <xsl:when test="$stringFunctionName = 'linoid'">3</xsl:when>
    </xsl:choose>
</xsl:template>



<!-- Function to get value converted to proper units.-->
<xsl:template name="convert">
    <xsl:param name="value" />
    <xsl:param name="quantity" />
    <xsl:choose>
        <xsl:when test="$xmlFileUnitSystem  = $targetUnitSystem"><xsl:value-of select="$value"/></xsl:when>
        
        <xsl:when test="$xmlFileUnitSystem  = 'Physiological Units' and $targetUnitSystem  = 'SI Units'">
            <xsl:choose>
                <xsl:when test="$quantity = 'Conductance Density'"><xsl:value-of select="number($value*10)"/></xsl:when>
                <xsl:when test="$quantity = 'Conductance'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Voltage'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvVoltage'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Time'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Length'"><xsl:value-of select="number($value div 100)"/></xsl:when> <!--Physiol len is cm!-->
                <xsl:when test="$quantity = 'InvTime'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Concentration'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvConcentration'"><xsl:value-of select="number($value div 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'Current'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvCurrent'"><xsl:value-of select="number($value div 1000000)"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="number($value)"/></xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        
        <xsl:when test="$xmlFileUnitSystem  = 'SI Units' and $targetUnitSystem  = 'Physiological Units'">
            <xsl:choose>
                <xsl:when test="$quantity = 'Conductance Density'"><xsl:value-of select="number($value div 10)"/></xsl:when>
                <xsl:when test="$quantity = 'Conductance'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Voltage'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvVoltage'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Time'"><xsl:value-of select="number($value * 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Length'"><xsl:value-of select="number($value * 100)"/></xsl:when>  <!--Physiol len is cm!-->
                <xsl:when test="$quantity = 'InvTime'"><xsl:value-of select="number($value div 1000)"/></xsl:when>
                <xsl:when test="$quantity = 'Concentration'"><xsl:value-of select="number($value div 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvConcentration'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'Current'"><xsl:value-of select="number($value div 1000000)"/></xsl:when>
                <xsl:when test="$quantity = 'InvCurrent'"><xsl:value-of select="number($value * 1000000)"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="number($value)"/></xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        
        <xsl:when test="$xmlFileUnitSystem  = 'SI Units'">si</xsl:when>
    </xsl:choose>
</xsl:template>



<!-- Function to get equation in GENESIS format, pre v1.7.3 format-->
<xsl:template name="generateOldEquation">
    <xsl:param name="name" />
    <xsl:param name="functionForm" />
    <xsl:param name="expression" />
    <xsl:param name="A_cml" />
    <xsl:param name="k_cml" />
    <xsl:param name="d_cml" />
    <xsl:choose>

        <xsl:when test="string-length($functionForm) &gt; 0"> <!-- So not an empty string-->
            // ChannelML form of equation: <xsl:value-of select="$name"/> = <xsl:value-of select="$expression" />, with params:
            // A = <xsl:value-of select="$A_cml"/>, k = <xsl:value-of select="$k_cml" />, d = <xsl:value-of
            select="$d_cml" />, in units: <xsl:value-of select="$xmlFileUnitSystem"/>

            <xsl:choose>
                <xsl:when test="string($name) = 'alpha' or string($name) = 'beta' or string($name) = 'gamma' or string($name) = 'zeta'">
            A = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$A_cml"/></xsl:with-param>
                    <xsl:with-param name="quantity">InvTime</xsl:with-param>
                </xsl:call-template>
                </xsl:when>
                <xsl:when test="string($name) = 'tau'">
            A = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$A_cml"/></xsl:with-param>
                    <xsl:with-param name="quantity">Time</xsl:with-param>
                </xsl:call-template>
                </xsl:when>
                <xsl:when test="string($name) = 'inf'">
            A = <xsl:value-of select="$A_cml"/>
                </xsl:when>
                <xsl:otherwise>
            A = <xsl:value-of select="$A_cml"/> // Warning: unrecognised rate variable! Don't know how to convert units!
                </xsl:otherwise>
            </xsl:choose>
            k = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$k_cml"/></xsl:with-param>
                    <xsl:with-param name="quantity">InvVoltage</xsl:with-param>
                </xsl:call-template>
            B = 1/k
            V0 = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$d_cml"/></xsl:with-param>
                    <xsl:with-param name="quantity">Voltage</xsl:with-param>
                </xsl:call-template><xsl:text>
            </xsl:text>

    <xsl:choose>
        <xsl:when test="$functionForm = 'exponential'">

            <xsl:value-of select="$name"/> = A * {exp {(v - V0) / B}}
        </xsl:when>
        <xsl:when test="$functionForm = 'sigmoid'">
            <xsl:value-of select="$name"/> = A / ( {exp {(v - V0) / B}} + 1)
        </xsl:when>
            <xsl:when test="$functionForm = 'linoid'">

            if ( {abs {(v - V0)/ B}} &lt; 1e-6)
                <xsl:value-of select="$name"/> = A * (1 + (v - V0)/B/2)
            else
                <xsl:value-of select="$name"/> = A * ((v - V0) / B) /(1 - {exp {-1 * (v - V0)/B}})
            end

        </xsl:when>
    </xsl:choose>
        </xsl:when>

            <!-- In the case when the info on the gate is missing -->
        <xsl:otherwise>
            <xsl:value-of select="$name"/> = 1 // Gate is not present, power should = 0 so value of <xsl:value-of
                            select="$name"/> is not relevant
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>


<!-- Function to get equation in GENESIS format, post v1.7.3 format-->
<xsl:template name="generateNewEquation">
    <xsl:param name="name" />
    <xsl:param name="functionForm" />
    <xsl:param name="rate" />
    <xsl:param name="scale" />
    <xsl:param name="midpoint" />
    <xsl:choose>

        <xsl:when test="string-length($functionForm) &gt; 0"> <!-- So not an empty string-->
            // ChannelML form of equation: <xsl:value-of select="$name"/> which is of form <xsl:value-of select="$functionForm" />, with params:
            // A = <xsl:value-of select="$rate"/>, B = <xsl:value-of select="$scale" />, Vhalf = <xsl:value-of
            select="$midpoint" />, in units: <xsl:value-of select="$xmlFileUnitSystem"/>

            <xsl:choose>
                <xsl:when test="string($name) = 'alpha' or string($name) = 'beta' or string($name) = 'gamma' or string($name) = 'zeta'">
            A = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$rate"/></xsl:with-param>
                    <xsl:with-param name="quantity">InvTime</xsl:with-param>
                </xsl:call-template>
                </xsl:when>
                <xsl:when test="string($name) = 'tau'">
            A = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$rate"/></xsl:with-param>
                    <xsl:with-param name="quantity">Time</xsl:with-param>
                </xsl:call-template>
                </xsl:when>
                <xsl:when test="string($name) = 'inf'">
            A = <xsl:value-of select="$rate"/>
                </xsl:when>
                <xsl:otherwise>
            A = <xsl:value-of select="$rate"/> // Warning: unrecognised rate variable! Don't know how to convert units!
                </xsl:otherwise>
            </xsl:choose>
            B = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$scale"/></xsl:with-param>
                    <xsl:with-param name="quantity">Voltage</xsl:with-param>
                </xsl:call-template>
            Vhalf = <xsl:call-template name="convert">
                    <xsl:with-param name="value"><xsl:value-of select="$midpoint"/></xsl:with-param>
                    <xsl:with-param name="quantity">Voltage</xsl:with-param>
                </xsl:call-template><xsl:text>
            </xsl:text>

    <xsl:choose>
        <xsl:when test="$functionForm = 'exponential'">

            <xsl:value-of select="$name"/> = A * {exp {(v - Vhalf) / B}}
        </xsl:when>
        <xsl:when test="$functionForm = 'sigmoid'">
            <xsl:value-of select="$name"/> = A / ( {exp {(v - Vhalf) / B}} + 1)
        </xsl:when>
            <xsl:when test="$functionForm = 'exp_linear'">

            if ( {abs {(v - Vhalf)/ B}} &lt; 1e-6)
                <xsl:value-of select="$name"/> = A * (1 + (v - Vhalf)/B/2)
            else
                <xsl:value-of select="$name"/> = A * ((v - Vhalf) / B) /(1 - {exp {-1 * (v - Vhalf)/B}})
            end

        </xsl:when>
    </xsl:choose>
        </xsl:when>

            <!-- In the case when the info on the gate is missing -->
        <xsl:otherwise>
            <xsl:value-of select="$name"/> = 1 // Gate is not present, power should = 0 so value of <xsl:value-of
                            select="$name"/> is not relevant
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>



<!-- Function to try to format the rate expression to something this simulator is a bit happier with-->
<xsl:template name="formatExpression">
    <xsl:param name="variable" />
    <xsl:param name="oldExpression" />
    <xsl:choose>
        <xsl:when test="contains($oldExpression, '?')">
    <!-- Expression contains a condition!!-->
    <xsl:variable name="ifTrue"><xsl:value-of select="substring-before(substring-after($oldExpression,'?'), ':')"/></xsl:variable>
    <xsl:variable name="ifFalse"><xsl:value-of select="substring-after($oldExpression,':')"/></xsl:variable>
    <xsl:variable name="condition"><xsl:value-of select="substring-before($oldExpression,'?')"/></xsl:variable>

            if (<xsl:value-of select="translate($condition,'()','{}')"/>)<xsl:text>
                </xsl:text><xsl:value-of select="$variable"/> = <xsl:value-of select="translate($ifTrue,'()','{}')"/>
            else<xsl:text>
                </xsl:text><xsl:value-of select="$variable"/> = <xsl:value-of select="translate($ifFalse,'()','{}')"/>
            end
        </xsl:when>
        <xsl:otherwise>
    <xsl:value-of select="$variable"/> = <xsl:value-of select="translate($oldExpression,'()','{}')"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

</xsl:stylesheet>