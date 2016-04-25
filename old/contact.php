<?
mysql_connect("localhost", "dyzio", "dyzio123");
mysql_select_db("dyzio");
mysql_query('SET NAMES latin2');
mysql_query("INSERT INTO visits (ip, page, browser, lang, referer, accept, proxy) VALUES ('".$_SERVER["REMOTE_ADDR"]."',
                                                                                          '".$_SERVER["REQUEST_URI"]."',
                                                                                          '".$_SERVER["HTTP_USER_AGENT"]."',
                                                                                          '".$_SERVER["HTTP_ACCEPT_LANGUAGE"]."',
									                  '".$_SERVER["HTTP_REFERER"]."',
									                  '".$_SERVER["HTTP_ACCEPT"]."',
									                  '".$_SERVER["HTTP_X_FORWARDED_FOR"]."')") or die(mysql_error());
if ($_GET["download"] == "6502") {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename=ip6502.pdf');
    header('Content-Transfer-Encoding: binary');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize("pdf/6502.pdf"));
    ob_clean();
    flush();
    readfile("pdf/6502.pdf");
    exit;
}
?>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=iso-8859-2">
<title>modelCHIP</title>
<link rel="icon" href="favicon.ico" type="image/x-icon">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="logo"><img src="/modelchip33.png"></div>
<div id="menu"><a href="/">Products</a></div>
<div id="menu"><a href="/services.php">Services</a></div>
<div id="menu"><a href="/contact.php">Contact</a></div>
<div id="menu"><a href="/about.php">About</a></div>
<? if($_SERVER["PHP_SELF"] == "/contact.php") { ?>
<div id="subpage">
    <p><span>Contact</span></p>
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d20382.03088063223!2d18.705119237776305!3d50.31518531547542!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x471131c5f7828911%3A0x706905f9236dce1c!2zTWljaGHFgmEgR3Jhxbx5xYRza2llZ28sIEdsaXdpY2U!5e0!3m2!1spl!2spl!4v1456734104279" width="425" height="350" frameborder="0" style="border:0" allowfullscreen></iframe>
    <div>
    <p>modelCHIP</p>
    <br>
    <a href="mailto:info@modelchip.com">info@modelchip.com</a><br>
    </div>
</div>
<? } elseif($_SERVER["PHP_SELF"] == "/services.php") { ?>
<div id="subpage">
    <p><span>Services</span></p>
    modelCHIP is offering a design services of any embedded products, starting from VHDL/Verilog RTL and testbench<br>
    modelling through FPGA prototyping ending at software driver development.<br>
    <br>
</div>
<? } elseif($_SERVER["PHP_SELF"] == "/about.php") { ?>
<div id="subpage">
    <p><span>About</span></p>
    modelCHIP is an IP vendor and embedded software company based in Gliwice, Poland.<br>
</div>
<? } else { ?>
<div id="subpage">
    <p><span>IP6502</span> - MOS Technology 6502 compliant IP core <a href="?download=6502"></a></p>
    <img id="ip6502" src="ip6502.svg">
    <div>
    <p>Overview</p>
    The IP6502 RTL HDL IP core implements the MOS Technology 6502 feature and instruction set.
    This fast 8-bit databus wide microprocessor is capable of running most of its instruction in two clock cycle, 
    with the most powerful direct and indirect zero-page addressing that are two bytes long.
    The external 64KB memory access is done via 16-bit wide address bus and 13 addressing modes for most of the instructions.
    External event interfacing is accomplished by separate non-maskable and maskable interrupt lines.
    Additional DMA modules can hold down the IP6502 core by the RDY line to allow memory access.
    Arithmetic is capable of signed, unsigned and BCD numbers manipulation.
    In order to communicate with external math unit the SO (Set Overflow) allows overflow flag setting.
    <p>Features</p>
    <ul>
    <li>56 instructions</li>
    <li>151 instruction opcodes</li>
    <li>13 addressing modes</li>
    <li>up to 64KB external memory</li>
    <li>16-bit wide address bus</li>
    <li>8-bit wide databus</li>
    <li>3 general purpose registers</li>
    <ul>
	<li>A - accumulator for most of the arithmetic</li>
	<li>X,Y - index registers for memory index based access</li>
    </ul>
    <li>NMI non-maskable and IRQ maskable interrupt inputs</li>
    <li>RDY line for DMA interfacing</li>
    </ul>
    <p>Deliverables</p>
    <ul>
    <li>Fully synthesizable VHDL/Verilog RTL core or reference technology netlist</li>
    <li>Complete testbench and reference chip waveforms to compare</li>
    <li>Full product documentation covering functionality and integration guideline</li>
    <li>Software development support</li>
    <li>IP core customization including new opcode specification</li>
    <li>Reference design
    </ul>
    <a href="?download=6502"><img src="pdf-icon.png" border="0" style="vertical-align: middle"></a> <a href="?download=6502">IP6502 Datasheet</a>
    </div>
</div>
<? } ?>
<br>
<div style="clear: both;">
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- Bottom -->
<ins class="adsbygoogle"
     style="display:inline-block;width:728px;height:90px"
     data-ad-client="ca-pub-6454993547239402"
     data-ad-slot="2864863974"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
</div>
</body>
