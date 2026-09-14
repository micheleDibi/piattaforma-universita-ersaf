import { Award, Building2, Check, Circle, GraduationCap, MapPin, User, UserCog, X } from "lucide-react";

export {
  ArrowLeft, ArrowUpFromLine, Award, Building2, ChevronRight, CircleAlert, CircleCheck, CircleUserRound,
  Eye, EyeOff, FileText, GraduationCap, Info, LayoutDashboard, LoaderCircle,
  LogOut, MapPin, Menu, Pencil, Plus, Search, SlidersHorizontal, Trash2, TriangleAlert, User, UserCog, Users,
} from "lucide-react";
export { Check, Circle, X };

export const ICONE_REGOLA_PASSWORD = { ok: Check, ko: X, neutro: Circle, non_verificabile: Circle };

export const ICONE_CAMPI_ELENCO = {
  universita: GraduationCap,
  sede: MapPin,
  azienda: Building2,
  ruolo: UserCog,
  cliente: User,
  corso: GraduationCap,
  tipo: Award,
};
