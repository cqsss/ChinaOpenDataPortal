package nju.websoft.chinaopendataportal.Util;

import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.web.servlet.HandlerInterceptor;

public class UserAgentInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        String userAgent = request.getHeader("User-Agent");
        if (userAgent == null || userAgent.isEmpty() || userAgent.contains("bot")
                || userAgent.matches(List.of(bots).stream().reduce("", (a, b) -> String.format("%s|%s", a, b)))) {
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            return false;
        }
        return true;
    }

    String[] bots = new String[] {
            "360Spider",
            "acapbot",
            "acoonbot",
            "ahrefs",
            "alexibot",
            "asterias",
            "attackbot",
            "backdorbot",
            "becomebot",
            "binlar",
            "blackwidow",
            "blekkobot",
            "blexbot",
            "blowfish",
            "bullseye",
            "bunnys",
            "butterfly",
            "careerbot",
            "casper",
            "checkpriv",
            "cheesebot",
            "cherrypick",
            "chinaclaw",
            "choppy",
            "clshttp",
            "cmsworld",
            "copernic",
            "copyrightcheck",
            "cosmos",
            "crescent",
            "cy_cho",
            "datacha",
            "demon",
            "diavol",
            "discobot",
            "dittospyder",
            "dotbot",
            "dotnetdotcom",
            "dumbot",
            "emailcollector",
            "emailsiphon",
            "emailwolf",
            "exabot",
            "extract",
            "eyenetie",
            "feedfinder",
            "flaming",
            "flashget",
            "flicky",
            "foobot",
            "g00g1e",
            "getright",
            "gigabot",
            "go-ahead-got",
            "gozilla",
            "grabnet",
            "grafula",
            "harvest",
            "heritrix",
            "httrack",
            "icarus6j",
            "jetbot",
            "jetcar",
            "jikespider",
            "kmccrew",
            "leechftp",
            "libweb",
            "linkextractor",
            "linkscan",
            "linkwalker",
            "loader",
            "masscan",
            "miner",
            "majestic",
            "mechanize",
            "mj12bot",
            "morfeus",
            "moveoverbot",
            "netmechanic",
            "netspider",
            "nicerspro",
            "nikto",
            "ninja",
            "nutch",
            "octopus",
            "pagegrabber",
            "planetwork",
            "postrank",
            "proximic",
            "purebot",
            "pycurl",
            "python",
            "queryn",
            "queryseeker",
            "radian6",
            "radiation",
            "realdownload",
            "rogerbot",
            "scooter",
            "seekerspider",
            "semalt",
            "siclab",
            "sindice",
            "sistrix",
            "sitebot",
            "siteexplorer",
            "sitesnagger",
            "skygrid",
            "smartdownload",
            "snoopy",
            "sosospider",
            "spankbot",
            "spbot",
            "sqlmap",
            "stackrambler",
            "stripper",
            "sucker",
            "surftbot",
            "sux0r",
            "suzukacz",
            "suzuran",
            "takeout",
            "teleport",
            "telesoft",
            "true_robots",
            "turingos",
            "turnit",
            "vampire",
            "vikspider",
            "voideye",
            "webleacher",
            "webreaper",
            "webstripper",
            "webvac",
            "webviewer",
            "webwhacker",
            "winhttp",
            "wwwoffle",
            "woxbot",
            "xaldon",
            "xxxyy",
            "yamanalab",
            "yioopbot",
            "youda",
            "zeus",
            "zmeu",
            "zune",
            "zyborg"
    };
}